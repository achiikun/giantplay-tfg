package cat.uab.giantplayadmin.model;

import android.util.Log;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.ScheduledThreadPoolExecutor;
import java.util.concurrent.TimeUnit;

import cat.uab.giantplayadmin.util.ConnectionManager;

public class GPUserImpl implements GPUser {

    public String key;
    public String name;
    public GPConnection connection;
    public int delay;

    private ScheduledExecutorService scheduledThreadPoolExecutor;

    public GPUserImpl(String key, String name, GPConnection connection){
        this.key = key;
        this.name = name;
        this.connection = connection;
        this.scheduledThreadPoolExecutor = Executors.newSingleThreadScheduledExecutor();
    }

    @Override
    public String getKey() {
        return key;
    }

    @Override
    public String getName() {
        return name;
    }

    @Override
    public int getDelay() {
        return delay;
    }

    @Override
    public void setDelay(int d) {
        delay = d;
    }

    @Override
    public GPParams getParams() {
        return null;
    }

    @Override
    public void setParams(GPParams params) {

    }

    @Override
    public void sendEvent(final String event, final double... values) {

        scheduledThreadPoolExecutor.schedule(new Runnable() {
            @Override
            public void run() {
                JSONArray jo = new JSONArray();
                try {
                    jo.put(key);
                    jo.put(event);

                    for(double d: values)
                        jo.put(d);

                } catch (JSONException e) {
                    e.printStackTrace();
                }

                Log.i("GPUserImpl", "Going to send: " + jo);

                ConnectionManager.getInstance().send(jo);
            }
        }, delay, TimeUnit.MILLISECONDS);

    }

    @Override
    public void sendEvent(final String event, final float... values) {

        scheduledThreadPoolExecutor.schedule(new Runnable() {
            @Override
            public void run() {
                JSONArray jo = new JSONArray();
                try {
                    jo.put(key);
                    jo.put(event);

                    for(double d: values)
                        jo.put(d);

                } catch (JSONException e) {
                    e.printStackTrace();
                }

                Log.i("GPUserImpl", "Going to send: " + jo);

                ConnectionManager.getInstance().send(jo);
            }
        }, delay, TimeUnit.MILLISECONDS);

    }

    @Override
    public void logout() {
        JSONObject jo = new JSONObject();
        try {
            jo.put("action", "logout");
            jo.put("key", key);
        } catch (JSONException e) {
            e.printStackTrace();
        }

        ConnectionManager.getInstance().send(jo);

    }

    @Override
    public String toString() {
        return "GPUserImpl{" +
                "key='" + key + '\'' +
                ", name='" + name + '\'' +
                ", delay=" + delay + '\'' +
                '}';
    }
}
