package cat.uab.giantplayadmin.wifi;

import android.util.Log;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.PrintWriter;
import java.net.InetAddress;
import java.net.Socket;

import cat.uab.giantplayadmin.model.GPConnection;
import cat.uab.giantplayadmin.util.ConnectionManager;

public class WifiGPConnection implements GPConnection {

    private Socket socket;
    private PrintWriter writer;
    private BufferedReader reader;
    private Thread listenerThread;

    public WifiGPConnection(InetAddress address, int port) {
        try {
            socket = new Socket(address, port);
            socket.setTcpNoDelay(true);

            this.writer = new PrintWriter(socket.getOutputStream(), true);
            this.reader = new BufferedReader(new InputStreamReader(socket.getInputStream()));

            this.listenerThread = new Thread(new Runnable() {
                @Override
                public void run() {
                    ConnectionManager.getInstance().onConnect(WifiGPConnection.this);
                    listenRun();
                }
            });
            this.listenerThread.start();

        } catch (IOException e) {
            e.printStackTrace();
            ConnectionManager.getInstance().onNotConnect(WifiGPConnection.this);
        }

    }

    private void listenRun() {

        try {

            while (true) {

                recieve();

            }

        }catch (IOException e){
            e.printStackTrace();
        }

        ConnectionManager.getInstance().onDisconnect(this);

    }

    public void recieve() throws IOException {

        String message = reader.readLine();
        Log.i("WifiGPConnection", "Recieved: " + message);

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
    public void send(JSONObject jo) {
        writer.write(jo.toString());
        writer.write("\n");
        writer.flush();
    }

    @Override
    public void send(JSONArray jo) {
        writer.write(jo.toString());
        writer.write("\n");
        writer.flush();
    }
}
