package cat.uab.giantplayadmin;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.hardware.SensorManager;
import android.text.InputType;
import android.util.AttributeSet;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.CompoundButton;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ListView;
import android.widget.NumberPicker;
import android.widget.TextView;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

import cat.uab.giantplayadmin.model.GPUser;
import cat.uab.giantplayadmin.util.ConnectionManager;

import static android.content.Intent.FLAG_ACTIVITY_CLEAR_TOP;
import static android.content.Intent.FLAG_ACTIVITY_SINGLE_TOP;
import static android.content.Intent.makeMainActivity;

public class UsersView extends FrameLayout {

    private Button button;
    private ListView listview;

    private ArrayAdapter<GPUser> adapter;
    private MainActivity activity;

    public Map<String, List<GPUser>> groups = new HashMap<>();

    public UsersView(Context context) {
        super(context);
        init(context);
    }

    public UsersView(Context context, AttributeSet attrs) {
        super(context, attrs);
        init(context);
    }

    public UsersView(Context context, AttributeSet attrs, int defStyle) {
        super(context, attrs, defStyle);
        init(context);
    }

    public void setActivity(MainActivity a){
        this.activity = a;
    }

    private void init(Context context) {
        inflate(context, R.layout.users_view, this);

        button = findViewById(R.id.btn_addplayer);
        button.setOnClickListener(new OnClickListener() {
            @Override
            public void onClick(View view) {
                AlertDialog alertDialog = new AlertDialog.Builder(getContext()).create();
                alertDialog.setTitle("New Player");
                alertDialog.setMessage("Insert player's name:");

                LinearLayout ll = new LinearLayout(getContext());
                ll.setOrientation(LinearLayout.VERTICAL);

                final EditText input = new EditText(getContext());
                input.setInputType(InputType.TYPE_CLASS_TEXT);

                final NumberPicker np = new NumberPicker(getContext());
                np.setMinValue(1);
                np.setMaxValue(50);
                np.setValue(1);
                np.setEnabled(false);

                TextView tv = new TextView(getContext());
                tv.setText("Clones?");

                final CheckBox cb = new CheckBox(getContext());
                cb.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
                    @Override
                    public void onCheckedChanged(CompoundButton compoundButton, boolean b) {
                    np.setEnabled(b);
                    }
                });

                ll.addView(input);
                ll.addView(tv);
                ll.addView(cb);
                ll.addView(np);

                alertDialog.setView(ll);

                alertDialog.setButton(AlertDialog.BUTTON_NEUTRAL, "OK",
                        new DialogInterface.OnClickListener() {
                            public void onClick(DialogInterface dialog, int which) {

                                if(cb.isChecked()){

                                    for(int i = 0; i < np.getValue(); i++){

                                        ConnectionManager.getInstance().send(
                                                ConnectionManager.getInstance().loginMessage(input.getText().toString() + " (" + (i+1) + ")")
                                        );

                                    }

                                }else{

                                    ConnectionManager.getInstance().send(
                                            ConnectionManager.getInstance().loginMessage(input.getText().toString())
                                    );
                                }



                                dialog.dismiss();
                            }
                        });

                alertDialog.show();

            }
        });

        listview = findViewById(R.id.lv_players);

        adapter = new ArrayAdapter<>(getContext(), android.R.layout.simple_list_item_1);
        listview.setAdapter(adapter);

        listview.setOnItemClickListener(new AdapterView.OnItemClickListener() {
            @Override
            public void onItemClick(AdapterView<?> adapterView, View view, int i, long l) {
                GPUser user = adapter.getItem(i);
                Intent in = new Intent(getContext(), PlayActivity.class);
                in.addFlags(FLAG_ACTIVITY_CLEAR_TOP | FLAG_ACTIVITY_SINGLE_TOP );
                in.putExtra("userkey", user.getKey());
                activity.startActivity(in);
            }
        });

        listview.setOnItemLongClickListener(new AdapterView.OnItemLongClickListener() {
            @Override
            public boolean onItemLongClick(AdapterView<?> adapterView, View view, int i, long l) {
                GPUser user = adapter.getItem(i);
                user.logout();
                return false;
            }

        });

    }

    public synchronized void addGPUser(GPUser user){
        String key = user.getName().split(" ")[0];

        int delay = -200;

        if(!groups.containsKey(key))
            groups.put(key, new ArrayList<GPUser>());
        else
            delay = groups.get(key).get(groups.get(key).size()-1).getDelay();

        user.setDelay(delay+200);

        groups.get(key).add(user);
        adapter.add(user);
    }

    public synchronized void removeGPUser(GPUser user){
        String key = user.getName().split(" ")[0];

        if(groups.containsKey(key))
            groups.get(key).remove(user);

        adapter.remove(user);
    }

    public void sendEvent(GPUser user, String event, double[] values) {
        String key = user.getName().split(" ")[0];
        List<GPUser> l = groups.get(key);

        for(GPUser u: l){
            u.sendEvent(event, values);
        }
    }

    public void sendEvent(GPUser user, String event, float[] values) {
        String key = user.getName().split(" ")[0];
        List<GPUser> l = groups.get(key);

        for(GPUser u: l){
            u.sendEvent(event, values);
        }
    }

    public void onEvent(GPUser user, String eventKey, float[] values) {

        PlayActivity pa = activity.playActivity;

        if(pa != null){
            if(pa.user == user){
                pa.onEvent(eventKey, values);
            }
        }
    }
}
