package hello.handler;

import java.io.IOException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;

import javax.servlet.ServletException;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

import org.eclipse.jetty.server.*;
import org.eclipse.jetty.server.handler.AbstractHandler;
import org.eclipse.jetty.server.handler.AbstractHandlerContainer;


/**
 * An implementation of the TechEmpower benchmark tests using the Jetty web
 * server.  
 */
public final class HelloWebServer 
{
    private static final boolean virtual = Boolean.valueOf(System.getProperty("virtual", "true"));

    public static void main(String[] args) throws Exception
    {
        Server server = new Server(8080);
        ServerConnector connector = new ServerConnector(server,
                virtual? Executors.newVirtualThreadPerTaskExecutor() : null, null, null, -1,-1, new HttpConnectionFactory());
        HttpConfiguration config = connector.getBean(HttpConnectionFactory.class).getHttpConfiguration();
        config.setSendDateHeader(true);
        config.setSendServerVersion(true);

        PathHandler pathHandler = new PathHandler();
        server.setHandler(pathHandler);
        server.setConnectors(new Connector[]{connector});

        server.start();
        server.join();
    }
    
    public static class PathHandler extends AbstractHandler
    {
        JsonHandler _jsonHandler=new JsonHandler();
        PlainTextHandler _plainHandler=new PlainTextHandler();
        
        public PathHandler()
        {
            addBean(_jsonHandler);
            addBean(_plainHandler);
        }

        @Override
        public void setServer(Server server)
        {
            super.setServer(server);
            _jsonHandler.setServer(server);
            _plainHandler.setServer(server);
        }

        @Override
        public void handle(String target, Request baseRequest, HttpServletRequest request, HttpServletResponse response) throws IOException, ServletException
        {
            if ("/plaintext".equals(target))
                _plainHandler.handle(target,baseRequest,request,response);
            else if ("/json".equals(target))
                _jsonHandler.handle(target,baseRequest,request,response);
        }
        
    }
}
