package cat.uab.giantplayadmin.model;

import android.support.v4.util.Consumer;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.IOException;

public interface GPConnection {

    void send(JSONObject jo);
    void send(JSONArray jo);

}
