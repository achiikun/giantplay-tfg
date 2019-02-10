package cat.uab.giantplayadmin.util;

import android.content.Context;
import android.graphics.Point;
import android.net.ConnectivityManager;
import android.net.NetworkInfo;
import android.net.wifi.WifiManager;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.net.InetAddress;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.Executor;
import java.util.concurrent.Executors;

import cat.uab.giantplayadmin.model.GPConnection;
import cat.uab.giantplayadmin.model.GPUser;
import cat.uab.giantplayadmin.model.GPUserImpl;

public class ConnectionManager implements ConnectTastListener {

    static final String ADMINKEY = "olakease";

    private static final ConnectionManager ourInstance = new ConnectionManager();
    private Map<String, GPUser> loggedUsers;
    private Context ctx;

    public static ConnectionManager getInstance() {
        return ourInstance;
    }

    private ConnectionManager() {
    }

    private GPConnection connection;
    private ConnectionManagerListener listener;

    private Thread listenerThread;

    private Executor executor = Executors.newSingleThreadExecutor();//.newCachedThreadPool();

    public void setListener(ConnectionManagerListener listener, Context ctx){
        this.listener = listener;
        this.ctx = ctx;
    }

    public void connect(){

        loggedUsers = new HashMap<>();

        WifiManager wifi = (WifiManager) ctx.getSystemService(Context.WIFI_SERVICE);

        ConnectivityManager connectivityManager = (ConnectivityManager)ctx
                .getSystemService(Context.CONNECTIVITY_SERVICE);
        NetworkInfo networkInfo = connectivityManager == null ? null : connectivityManager.getActiveNetworkInfo();

        UDPConnectTask udp = new UDPConnectTask(this, wifi, networkInfo);
        udp.execute();

    }

    public boolean isConnected(){

        return connection != null;
    }

    public void execute(Runnable run){
        executor.execute(run);
    }

    public JSONObject loginMessage(String name) {

        JSONObject jo = new JSONObject();

        try {
            jo.put("action", "login");
            jo.put("name", name);
            jo.put("type", "smartphone");

            JSONObject props = new JSONObject();
            Point size = listener.getWindowSize();
            props.put("screenw", size.x);
            props.put("screenh", size.y);

            jo.put("props", props);

           return jo;

        } catch (JSONException e) {
            e.printStackTrace();
        }

        return null;
    }

    public JSONObject adminMessage() {

        JSONObject jo = new JSONObject();

        try {
            jo.put("action", "admin");
            jo.put("adminkey", ADMINKEY);

            return jo;

        } catch (JSONException e) {
            e.printStackTrace();
        }

        return null;
    }

    public JSONObject gameMessage(String key) {
        JSONObject jo = new JSONObject();

        try {
            jo.put("action", "admin");
            jo.put("adminkey", ADMINKEY);
            jo.put("game", key);

            return jo;

        } catch (JSONException e) {
            e.printStackTrace();
        }

        return null;
    }

    @Override
    public void onPreFind() {
        listener.onPreFind();
    }

    @Override
    public void onFind(InetAddress address, int port) {
        listener.onFind(address, port);
    }

    public void onConnect(final GPConnection connection) {
        this.connection = connection;
        listener.onConnect();
    }

    public void onNotConnect(GPConnection connection) {
        this.connection = null;
        listener.onDisconnect();
    }

    public void onDisconnect(GPConnection connection) {
        this.connection = null;
        listener.onDisconnect();
    }

    @Override
    public void onNotFind() {
        listener.onNotFind();
    }

    public void onMessage(JSONObject jo){
        try {
            String a = jo.getString("action");

            if(a != null){
                switch (a){
                    case "login":
                        listenLogin(jo);
                        break;
                    case "logout":
                        listenLogout(jo);
                        break;
                    case "admin":
                        listenAdmin(jo);
                        break;
                }
            }

        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    public void onMessage(JSONArray ja){
        try {
            String userKey = ja.getString(0);
            String userEvent = ja.getString(1);

            float[] values = new float[ja.length()-2];

            for (int i = 2; i < ja.length(); i++) {
                values[i-2] = (float) ja.getDouble(i);
            }

            listenEvent(userKey, userEvent, values);

        } catch (JSONException e) {
            e.printStackTrace();
        }
    }

    private void listenEvent(String userKey, String eventKey, float[] values) {
        GPUser user = loggedUsers.get(userKey);
        if(user != null){
            listener.onEvent(user, eventKey, values);
        }
    }

    private void listenAdmin(JSONObject jo) {
        listener.onAdmin(jo);
    }

    private void listenLogin(JSONObject jo) throws JSONException {

        String key = jo.getString("key");
        String name = jo.getString("name");

        GPUser user = new GPUserImpl(key,name, connection);
        loggedUsers.put(key, user);
        listener.onLogin(user);
    }

    private void listenLogout(JSONObject jo) throws JSONException {

        String key = jo.getString("key");

        GPUser user = loggedUsers.get(key);

        if(user != null){
            loggedUsers.remove(key);
            listener.onLogout(user);
        }
    }

    public void send(final JSONObject jo) {
        execute(new Runnable() {
            @Override
            public void run() {
                connection.send(jo);
            }
        });
    }

    public void send(final JSONArray jo) {
        execute(new Runnable() {
            @Override
            public void run() {
                System.out.println(System.currentTimeMillis());
                GPConnection c = connection;
                if(c != null)
                    c.send(jo);
            }
        });
    }

    public GPUser getUser(String key) {
        return loggedUsers.get(key);
    }

    public void sendEvent(GPUser user, String event, double... values) {
        listener.sendEvent(user, event, values);
    }

    public void sendEvent(GPUser user, String event, float... values) {
        listener.sendEvent(user, event, values);
    }

}
