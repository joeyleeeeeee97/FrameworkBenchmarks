package hello;

import java.net.InetSocketAddress;
import java.util.concurrent.ScheduledThreadPoolExecutor;
import java.util.concurrent.ThreadFactory;

import io.netty.bootstrap.ServerBootstrap;
import io.netty.channel.Channel;
import io.netty.channel.ChannelOption;
import io.netty.channel.EventLoopGroup;
import io.netty.channel.ServerChannel;
import io.netty.channel.epoll.Epoll;
import io.netty.channel.epoll.EpollChannelOption;
import io.netty.channel.epoll.EpollEventLoopGroup;
import io.netty.channel.epoll.EpollServerSocketChannel;
import io.netty.channel.kqueue.KQueue;
import io.netty.channel.kqueue.KQueueServerSocketChannel;
import io.netty.channel.nio.NioEventLoopGroup;
import io.netty.channel.oio.OioEventLoopGroup;
import io.netty.channel.socket.nio.NioServerSocketChannel;
import io.netty.channel.socket.oio.OioServerSocketChannel;
import io.netty.incubator.channel.uring.IOUring;
import io.netty.incubator.channel.uring.IOUringChannelOption;
import io.netty.incubator.channel.uring.IOUringEventLoopGroup;
import io.netty.incubator.channel.uring.IOUringServerSocketChannel;
import io.netty.util.ResourceLeakDetector;
import io.netty.util.ResourceLeakDetector.Level;

public class HelloWebServer {

	private static boolean virtual = Boolean.valueOf(System.getProperty("virtual", "false"));
	private static boolean oio = Boolean.valueOf(System.getProperty("oio", "true"));

	static {
		ResourceLeakDetector.setLevel(Level.DISABLED);
	}

	private final int port;

	public HelloWebServer(int port) {
		this.port = port;
	}

	public void run() throws Exception {
		ThreadFactory factory = virtual? Thread.ofVirtual().factory() : Thread.ofPlatform().factory();

		// Configure the server.
		if (oio) {
			doRun(new OioEventLoopGroup(2000, factory), OioServerSocketChannel.class, IoMultiplexer.EPOLL);
		} else if (IOUring.isAvailable()) {
			doRun(new IOUringEventLoopGroup(factory), IOUringServerSocketChannel.class, IoMultiplexer.IO_URING);
		} else
			if (Epoll.isAvailable()) {
			doRun(new EpollEventLoopGroup(factory), EpollServerSocketChannel.class, IoMultiplexer.EPOLL);
		} else if (KQueue.isAvailable()) {
			doRun(new EpollEventLoopGroup(factory), KQueueServerSocketChannel.class, IoMultiplexer.KQUEUE);
		} else {
			doRun(new NioEventLoopGroup(factory), NioServerSocketChannel.class, IoMultiplexer.JDK);
		}
	}

	private void doRun(EventLoopGroup loupGroup, Class<? extends ServerChannel> serverChannelClass, IoMultiplexer multiplexer) throws InterruptedException {
		try {
			InetSocketAddress inet = new InetSocketAddress(port);
			
			System.out.printf("Using %s IoMultiplexer%n", multiplexer);

			ServerBootstrap b = new ServerBootstrap();

			if (multiplexer == IoMultiplexer.EPOLL) {
				b.option(EpollChannelOption.SO_REUSEPORT, true);
			}
			
			if (multiplexer == IoMultiplexer.IO_URING) {
				b.option(IOUringChannelOption.SO_REUSEPORT, true);
			}
			
			b.option(ChannelOption.SO_BACKLOG, 8192);
			b.option(ChannelOption.SO_REUSEADDR, true);
			if (oio) {
				ThreadFactory factory = virtual? Thread.ofVirtual().factory() : Thread.ofPlatform().factory();
				b.group(loupGroup).channel(serverChannelClass).childHandler(new HelloServerInitializer(new ScheduledThreadPoolExecutor(100, factory)));
			} else {
				b.group(loupGroup).channel(serverChannelClass).childHandler(new HelloServerInitializer(loupGroup.next()));
			}
			b.childOption(ChannelOption.SO_REUSEADDR, true);

			Channel ch = b.bind(inet).sync().channel();

			System.out.printf("Httpd started. Listening on: %s%n", inet.toString());

			ch.closeFuture().sync();
		} finally {
			loupGroup.shutdownGracefully().sync();
		}
	}

	public static void main(String[] args) throws Exception {
		int port;
		if (args.length > 0) {
			port = Integer.parseInt(args[0]);
		} else {
			port = 8080;
		}
		new HelloWebServer(port).run();
	}
}
