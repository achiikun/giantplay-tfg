package cat.uab.giantplayadmin;

import android.app.ProgressDialog;
import android.content.Intent;
import android.graphics.Point;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.util.Log;
import android.view.Display;
import android.widget.TabHost;
import android.widget.Toast;

import org.json.JSONArray;
import org.json.JSONObject;

import java.net.InetAddress;
import java.net.URISyntaxException;
import java.util.ArrayList;
import java.util.List;

import cat.uab.giantplayadmin.model.GPConnection;
import cat.uab.giantplayadmin.model.GPGame;
import cat.uab.giantplayadmin.model.GPUser;
import cat.uab.giantplayadmin.util.ConnectionManager;
import cat.uab.giantplayadmin.util.ConnectionManagerListener;
import cat.uab.giantplayadmin.util.PermissionListener;
import cat.uab.giantplayadmin.util.PermissionUtil;
import cat.uab.giantplayadmin.websocket.WebSocketConnection;
import cat.uab.giantplayadmin.wifi.WifiGPConnection;

import static android.content.Intent.FLAG_ACTIVITY_CLEAR_TOP;

public class MainActivity extends AppCompatActivity implements ConnectionManagerListener, PermissionListener {

    public static PlayActivity playActivity = null;

    private TabHost tabHost;
    private ProgressDialog progressDialog;

    private AdminView admin;
    private UsersView users;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        PermissionUtil.getInstance().setListener(this);
        ConnectionManager.getInstance().setListener(this, this);

        admin = findViewById(R.id.tab1);
        users = findViewById(R.id.tab2);

        admin.setActivity(this);
        users.setActivity(this);

        if(savedInstanceState == null)
            PermissionUtil.getInstance().checkPermission(this);
    }

    @Override
    public void permissionGranted() {
        setTabs();
        ConnectionManager.getInstance().connect();
    }

    @Override
    public void permissionNotGranted() {
        Toast.makeText(this, "Need Internet to connect", Toast.LENGTH_SHORT).show();
        finish();
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String permissions[], int[] grantResults) {
        PermissionUtil.getInstance().onRequestPermissionResult(requestCode, permissions, grantResults);
    }

    private void setTabs() {
        tabHost = findViewById(R.id.tabhost);
        tabHost.setup();

        TabHost.TabSpec spec;

        spec = tabHost.newTabSpec("tab1")
                .setIndicator("Admin")
                .setContent(R.id.tab1);
        tabHost.addTab(spec);

        spec = tabHost.newTabSpec("tab2")
                .setIndicator("Players")
                .setContent(R.id.tab2);
        tabHost.addTab(spec);

        tabHost.setCurrentTab(0);
    }

    @Override
    public void onPreFind() {
        progressDialog = ProgressDialog.show(this, null, "Connecting by Wifi");
    }

    @Override
    public void onFind(InetAddress address, int port) {
        Log.d("UDPConnectTask", "Start TCP socket: " + address);

        try {
            GPConnection gp = new WifiGPConnection(address, port);
        } catch (Exception e) {
            e.printStackTrace();
        }

    }

    @Override
    public void onNotFind() {
        progressDialog.dismiss();
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                Toast.makeText(MainActivity.this, "Not Connected!", Toast.LENGTH_SHORT).show();
                finish();
            }
        });
    }

    @Override
    public Point getWindowSize() {

        Display display = getWindowManager().getDefaultDisplay();
        Point size = new Point();
        display.getSize(size);

        return size;
    }

    @Override
    public void onConnect() {
        try {
            Thread.sleep(100);
        } catch (InterruptedException e) {
            e.printStackTrace();
        }

        progressDialog.dismiss();
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                Toast.makeText(MainActivity.this, "Connected!", Toast.LENGTH_SHORT).show();

            }
        });

        ConnectionManager.getInstance().send(ConnectionManager.getInstance().loginMessage("Dummy User"));
        ConnectionManager.getInstance().send(ConnectionManager.getInstance().adminMessage());
    }


    @Override
    public void onDisconnect() {
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                Toast.makeText(MainActivity.this, "Was Disconnected!", Toast.LENGTH_SHORT).show();
                if(playActivity != null)
                    playActivity.finish();
                finish();
            }
        });
    }

    @Override
    public void onLogin(final GPUser user) {
        System.out.println("onLogin: " + user);
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                users.addGPUser(user);
            }
        });
    }

    @Override
    public void onLogout(final GPUser user) {
        System.out.println("onLogin: " + user);
        runOnUiThread(new Runnable() {
            @Override
            public void run() {
                users.removeGPUser(user);
            }
        });
    }

    @Override
    public void onAdmin(JSONObject admin) {
        if(admin.has("games")){
            try{

                List<GPGame> games = new ArrayList<>();
                JSONArray ja = admin.getJSONArray("games");
                for (int i = 0; i < ja.length(); i++) {
                    JSONObject jo = ja.getJSONObject(i);

                    games.add(new GPGame(
                            jo.getString("key"),
                            jo.getString("name")
                    ));

                }
                this.admin.setGames(games);

            }catch(Exception e){
                e.printStackTrace();
            }
        }
    }

    @Override
    public void onEvent(GPUser user, String eventKey, float[] values) {
        users.onEvent(user, eventKey, values);
    }

    @Override
    public void sendEvent(GPUser user, String event, double[] values) {
        users.sendEvent(user, event, values);
    }

    @Override
    public void sendEvent(GPUser user, String event, float[] values) {
        users.sendEvent(user, event, values);
    }
}
