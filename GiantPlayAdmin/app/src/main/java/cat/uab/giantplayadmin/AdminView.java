package cat.uab.giantplayadmin;

import android.content.Context;
import android.content.Intent;
import android.util.AttributeSet;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.FrameLayout;
import android.widget.ListView;

import java.util.List;

import cat.uab.giantplayadmin.model.GPGame;
import cat.uab.giantplayadmin.model.GPUser;
import cat.uab.giantplayadmin.util.ConnectionManager;

import static android.content.Intent.FLAG_ACTIVITY_CLEAR_TOP;
import static android.content.Intent.FLAG_ACTIVITY_SINGLE_TOP;

public class AdminView extends FrameLayout {


    private ListView listview;
    private ArrayAdapter<GPGame> adapter;

    private MainActivity activity;

    public AdminView(Context context) {
        super(context);
        inflate(context, R.layout.admin_view, this);
        init();
    }

    public void setActivity(MainActivity a){
        this.activity = a;
    }

    private void init() {
        listview = findViewById(R.id.list_of_games);

        adapter = new ArrayAdapter<>(getContext(), android.R.layout.simple_list_item_1);
        listview.setAdapter(adapter);

        listview.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
                GPGame user = adapter.getItem(i);

                ConnectionManager.getInstance().send(
                        ConnectionManager.getInstance().gameMessage(user.key)
                );

            }
        });
    }

    public AdminView(Context context, AttributeSet attrs) {
        super(context, attrs);
        inflate(context, R.layout.admin_view, this);
        init();
    }

    public AdminView(Context context, AttributeSet attrs, int defStyle) {
        super(context, attrs, defStyle);
        inflate(context, R.layout.admin_view, this);
        init();
    }

    public void setGames(final List<GPGame> games){
        activity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                adapter.clear();
                adapter.addAll(games);
            }
        });

    }

}
