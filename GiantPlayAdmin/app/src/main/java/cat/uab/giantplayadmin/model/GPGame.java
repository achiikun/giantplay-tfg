package cat.uab.giantplayadmin.model;

import android.util.Log;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.concurrent.Executors;
import java.util.concurrent.ScheduledExecutorService;
import java.util.concurrent.TimeUnit;

import cat.uab.giantplayadmin.util.ConnectionManager;

public class GPGame {

    public String key;
    public String name;

    public GPGame(String key, String name){
        this.key = key;
        this.name = name;
    }

    public String getKey() {
        return key;
    }

    public String getName() {
        return name;
    }

    @Override
    public String toString() {
        return "GPGame{" +
                "key='" + key + '\'' +
                ", name='" + name + '\'' +
                '}';
    }
}
