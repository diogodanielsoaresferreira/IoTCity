package com.example.iot.iot_city_manager;

import android.content.Intent;
import android.graphics.Color;
import android.support.annotation.MainThread;
import android.support.annotation.NonNull;
import android.support.design.widget.NavigationView;
import android.support.v4.view.GravityCompat;
import android.support.v4.widget.DrawerLayout;
import android.support.v7.app.ActionBarDrawerToggle;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.support.v7.widget.Toolbar;
import android.util.Log;
import android.view.Gravity;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.ImageButton;
import android.widget.TableLayout;
import android.widget.TableRow;
import android.widget.TextView;
import android.widget.Toast;

import com.android.volley.AuthFailureError;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.StringRequest;
import com.android.volley.toolbox.Volley;
import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.util.HashMap;
import java.util.Map;

public class AlertsActivity extends AppCompatActivity implements NavigationView.OnNavigationItemSelectedListener {
    private static final String TAG = "AlertsActivity";
    private static final String URL = "http://178.62.255.129/alerts/triginfo";
    private TableLayout tableLayout;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_alerts);

        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        // Table
        tableLayout  = (TableLayout) findViewById(R.id.alerts_header);

        // Navigation drawer
        NavigationView navigationView = (NavigationView) findViewById(R.id.nav_view);
        navigationView.setNavigationItemSelectedListener(this);

        View decorView = getWindow().getDecorView();
        // Hide the status bar.
        int uiOptions = View.SYSTEM_UI_FLAG_VISIBLE;
        decorView.setSystemUiVisibility(uiOptions);


        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        ActionBarDrawerToggle toggle = new ActionBarDrawerToggle(this, drawer,
                toolbar,
                R.string.navigation_drawer_open,
                R.string.navigation_drawer_close) {
        };

        drawer.addDrawerListener(toggle);
        toggle.syncState();

        // Alerts
        getAlerts();
    }

    @Override
    public boolean onNavigationItemSelected(@NonNull MenuItem item) {
        // Handle navigation view item clicks here.
        int id = item.getItemId();  //get the id of the item clicked
        Intent intent;
        switch (id) {
            case R.id.nav_dashboard:
                intent = new Intent(this, MainActivity.class);
                intent.setFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);
                startActivityIfNeeded(intent, 0);   //Launch main activity
                break;
            //If clicked on the map item
            case R.id.nav_map:
                intent = new Intent(this, MapsActivity.class);
                intent.setFlags(Intent.FLAG_ACTIVITY_REORDER_TO_FRONT);
                startActivityIfNeeded(intent, 0);   //Launch map activity
                break;
            //If clicked on the temperature item
            case R.id.temperature:
                intent = new Intent(this, Temperature.class);
                startActivity(intent);   //Launch detail temperature activity
                break;
            //If clicked on the noise item
            case R.id.noise:
                intent = new Intent(this, Noise.class);
                startActivity(intent);   //Launch detail noise activity
                break;
            //If clicked on the lighting item
            case R.id.lighting:
                intent = new Intent(this, Lighting.class);
                startActivity(intent);   //Launch detail lighting activity
                break;
            //If clicked on the UV radiaition item
            case R.id.radiation:
                intent = new Intent(this, UV_Radiation.class);
                startActivity(intent);   //Launch detail UV radiation activity
                break;
            //If clicked on the waste item
            case R.id.waste:
                intent = new Intent(this, Waste.class);
                startActivity(intent);   //Launch detail waste activity
                break;
            //If clicked on the people item
            case R.id.people:
                intent = new Intent(this, People.class);
                startActivity(intent);   //Launch detail people activity
                break;
            //If clicked on the help item
            case R.id.help:
                intent = new Intent(this, Help.class);
                startActivity(intent);   //Launch help activity
                break;
            //If clicked on the air item
            case R.id.air:
                intent = new Intent(this, Air.class);
                startActivity(intent);   //Launch detail air activity
                break;
            default:
                break;
        }
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        drawer.closeDrawer(GravityCompat.START);
        return true;
    }

    private void getAlerts() {
        JsonObjectRequest jsonArrayRequest = new JsonObjectRequest(Request.Method.GET, URL, null,
                new Response.Listener<JSONObject>() {
                    @Override
                    public void onResponse(JSONObject response) {
                        try {

                            JSONArray responseArray = response.getJSONArray("occurrences");
                            fillTable(responseArray);
                        }
                        catch (JSONException e) {
                            e.printStackTrace();
                        }
                    }
                },
                new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        Log.d(TAG,error.toString());
                    }
                }
        );

        VolleySingleton.getInstance(this).addToRequestQueue(jsonArrayRequest);
    }

    private void dismissAlert(final int alert_id) {
        String URL = "http://178.62.255.129/alerts/state/" + alert_id + "/SE";
        StringRequest stringRequest = new StringRequest(Request.Method.POST, URL,
                new Response.Listener<String>() {
                    @Override
                    public void onResponse(String response) {
                        try {
                            JSONObject resp = new JSONObject(response);
                            String status = resp.getString("status");
                            String info = resp.getString("info");
                            if(status.equals("Success")) {
                                TableRow row = (TableRow)findViewById(alert_id);
                                tableLayout.removeView(row);
                                Toast.makeText(AlertsActivity.this, info, Toast.LENGTH_LONG).show();
                            } else {
                                Toast.makeText(AlertsActivity.this, info, Toast.LENGTH_LONG).show();
                            }
                        } catch (JSONException e) {
                            e.printStackTrace();
                        }
                    }
                }, new Response.ErrorListener() {
                    @Override
                    public void onErrorResponse(VolleyError error) {
                        Log.d("Alert change post error", error.getCause().toString());
                    }
        }
        );
        VolleySingleton.getInstance(this).addToRequestQueue(stringRequest);
    }

    public void fillTable(JSONArray alerts)
    {
        if(alerts.length() == 0) {
            Log.d(TAG, "No triggered alerts");
            return;
        }

        for(int i = 0; i < alerts.length(); i++) {
            try {
                JSONObject alert = alerts.getJSONObject(i);
                // New row
                TableRow tr = new TableRow(this);
                tr.setId(alert.getInt("id"));
                tr.setPadding(0, 0, 2, 2);
                // Text views
                TextView c1 = new TextView(this);
                c1.setText(alert.getString("name"));

                TextView c2 = new TextView(this);
                JSONArray sensors = alert.getJSONArray("sensors");
                String sen_view = "";
                for (int j = 0; j <  sensors.length(); j++) {
                    sen_view += sensors.get(j).toString();
                    if(j != sensors.length() - 1)
                        sen_view += ", ";
                }
                c2.setText(sen_view);

                TextView c3 = new TextView(this);
                String date = alert.get("peak_date").toString();
                String strings[] = date.split("T");
                String point[] = strings[1].split("\\.");
                c3.setText(strings[0]+", "+point[0]);

                TextView c4 = new TextView(this);
                String threshold = alert.getString("threshold") + " (" +alert.getString("maximum_minimum") + " )";
                c4.setText(threshold);

                TextView c5 = new TextView(this);
                c5.setText(alert.get("peak").toString());

                // location button
                final Button button = new Button(getApplicationContext());
                button.setId(alert.getInt("id"));
                button.setText("Dismiss");
                button.setOnClickListener(new Button.OnClickListener(){
                    public void onClick(View v) {
                        dismissAlert(button.getId());
                    }
                });

                TableRow.LayoutParams params = new TableRow.LayoutParams(0, Toolbar.LayoutParams.MATCH_PARENT);
                params.setMargins(0,0,2,0);
                c1.setLayoutParams(params);
                c1.setGravity(Gravity.CENTER);
                c2.setLayoutParams(params);
                c2.setGravity(Gravity.CENTER);
                c3.setLayoutParams(params);
                c3.setGravity(Gravity.CENTER);
                c4.setLayoutParams(params);
                c4.setGravity(Gravity.CENTER);
                c5.setLayoutParams(params);
                c5.setGravity(Gravity.CENTER);
                button.setLayoutParams(params);
                // Add views
                tr.addView(c1);
                tr.addView(c2);
                tr.addView(c3);
                tr.addView(c4);
                tr.addView(c5);
                tr.addView(button);
                tableLayout.addView(tr);
            } catch (JSONException e) {
                e.printStackTrace();
            }
        }
    }
}