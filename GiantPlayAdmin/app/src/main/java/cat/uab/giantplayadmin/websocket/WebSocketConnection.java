package cat.uab.giantplayadmin.websocket;

import android.util.Log;

import org.java_websocket.client.WebSocketClient;
import org.java_websocket.drafts.Draft_6455;
import org.java_websocket.handshake.ServerHandshake;
import org.java_websocket.server.WebSocketServer;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.Inet4Address;
import java.net.InetAddress;
import java.net.Socket;
import java.net.URI;
import java.net.URISyntaxException;
import java.util.Collections;

import cat.uab.giantplayadmin.model.GPConnection;
import cat.uab.giantplayadmin.util.ConnectionManager;

public class WebSocketConnection extends WebSocketClient implements GPConnection {

    public WebSocketConnection(InetAddress address, int port) throws URISyntaxException {
        super(new URI( "ws://" + address.getCanonicalHostName() + ":" + port ), new Draft_6455());
        Log.i("WebSocketConnection", "ws://" + address.getCanonicalHostName() + ":" + port);
        connect();
    }

    @Override
    public void send(JSONObject jo) {
        send(jo.toString());
    }

    @Override
    public void send(JSONArray jo) {
        send(jo.toString());
    }

    @Override
    public void onOpen(ServerHandshake handshakedata) {
        Log.i("WebSocketConnection", "onOpen");
        ConnectionManager.getInstance().onConnect(this);
    }

    @Override
    public void onMessage(String message) {
        Log.i("WebSocketConnection", "onMessage");

        try {
            JSONObject jo = new JSONObject(message);
            ConnectionManager.getInstance().onMessage(jo);
        } catch (JSONException e) {
            try {
                JSONArray jo = new JSONArray(message);
                ConnectionManager.getInstance().onMessage(jo);
            } catch (JSONException e2) {
                e2.printStackTrace();
            }
        }

    }

    @Override
    public void onClose(int code, String reason, boolean remote) {
        Log.i("WebSocketConnection", "onClose");

        ConnectionManager.getInstance().onDisconnect(this);
    }

    @Override
    public void onError(Exception ex) {
        Log.i("WebSocketConnection", "onError");
        ex.printStackTrace();

        ConnectionManager.getInstance().onDisconnect(this);
    }
}
