package com.example.iot.iot_city_manager;

import android.Manifest;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.drawable.Drawable;
import android.location.Location;
import android.os.AsyncTask;
import android.os.Build;
import android.os.Bundle;
import android.provider.Settings;
import android.support.annotation.NonNull;
import android.support.v4.app.ActivityCompat;
import android.support.v4.content.ContextCompat;
import android.support.v4.widget.SwipeRefreshLayout;
import android.util.Log;
import android.view.View;
import android.support.design.widget.NavigationView;
import android.support.v4.view.GravityCompat;
import android.support.v4.widget.DrawerLayout;
import android.support.v7.app.ActionBarDrawerToggle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.Menu;
import android.view.MenuItem;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.RelativeLayout;
import android.widget.TextView;
import com.google.android.gms.common.ConnectionResult;
import com.google.android.gms.common.api.GoogleApiClient;
import com.google.android.gms.location.LocationListener;
import com.google.android.gms.location.LocationRequest;
import com.google.android.gms.location.LocationServices;
import org.json.JSONException;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import android.os.Handler;
import android.widget.Toast;

public class MainActivity extends AppCompatActivity
        implements NavigationView.OnNavigationItemSelectedListener, GoogleApiClient.ConnectionCallbacks, GoogleApiClient.OnConnectionFailedListener, LocationListener {

    private static final String TAG = "MainActivity";
    private GoogleApiClient mGoogleApiClient;
    private LocationRequest locationRequest;
    private Location mCurrentLocation;
    private boolean listeningToChanges = false;
    private Menu menu = null;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);
        Drawable drawable = ContextCompat.getDrawable(getApplicationContext(),R.drawable.ic_mode_edit_white_24dp);
        toolbar.setOverflowIcon(drawable);

        // navigation drawer support
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        ActionBarDrawerToggle toggle = new ActionBarDrawerToggle(
                this, drawer, toolbar, R.string.navigation_drawer_open, R.string.navigation_drawer_close);
        drawer.addDrawerListener(toggle);
        toggle.syncState();

        NavigationView navigationView = (NavigationView) findViewById(R.id.nav_view);
        navigationView.setNavigationItemSelectedListener(this);

        // gps
        mGoogleApiClient = new GoogleApiClient.Builder(this)
                .addApi(LocationServices.API)
                .addConnectionCallbacks(this)
                .addOnConnectionFailedListener(this)
                .build();

        // Time intervals
        locationRequest = new LocationRequest();
        locationRequest.setInterval(10000);
        locationRequest.setFastestInterval(5000);
        locationRequest.setPriority(LocationRequest.PRIORITY_HIGH_ACCURACY);

        final SwipeRefreshLayout swipeView = (SwipeRefreshLayout) findViewById(R.id.content_main1);

        // Add swipe to refresh data on dashboard
        swipeView.setOnRefreshListener(new SwipeRefreshLayout.OnRefreshListener(){
            @Override
            public void onRefresh() {
                swipeView.setRefreshing(true);
                Log.d(TAG, "Refreshing dashboard");
                (new Handler()).postDelayed(new Runnable() {
                    @Override
                    public void run() {
                        swipeView.setRefreshing(false);
                        new PopulateMainMetrics().execute();
                    }
                }, 2000);
            }
        });
    }

    @Override
    protected void onStart() {
        super.onStart();
        // Connect gps on start
        mGoogleApiClient.connect();
    }

    @Override
    protected void onResume() {
        super.onResume();
        // Start listening to changes on resume
        if(mGoogleApiClient.isConnected() && !listeningToChanges) {
            Log.d(TAG, "Requesting updates on resume");
            requestLocationUpdates();
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        // Stop listening to changes on pause
        if (mGoogleApiClient.isConnected() && listeningToChanges) {
            stopLocationUpdates();
            Log.d(TAG, "Stopped listening to changes on pause");
        }
    }

    @Override
    protected void onStop() {
        super.onStop();
        // Disconnect gps on stop
        mGoogleApiClient.disconnect();
        Log.d(TAG, "GPS disconnected");
    }

    @Override
    public void onBackPressed() {
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        if (drawer.isDrawerOpen(GravityCompat.START)) {
            drawer.closeDrawer(GravityCompat.START);
        } else {
            super.onBackPressed();
        }
    }

    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        // Inflate the menu; this adds items to the action bar if it is present.
        getMenuInflater().inflate(R.menu.menu_main, menu);
        this.menu = menu;
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        // return super.onOptionsItemSelected(item);
        switch (item.getItemId()) {
            //If clicked in the temperature checkbox
            case R.id.temperature_1:
                LinearLayout lrl = (LinearLayout) findViewById(R.id.rl_temp);   //Get the temperature square id in the dashboard
                if(item.isChecked()) {  //If checkbox is already checked
                    item.setChecked(false); //Uncheck it
                    lrl.setVisibility(View.GONE);   //Make temperature square in the dashboard disappear
                    MenuItem it = menu.findItem(R.id.all);
                    it.setChecked(false);
                }
                //If it is not checked
                else {
                    item.setChecked(true);  //Check it
                    lrl.setVisibility(View.VISIBLE);    //Make temperature square appear in the dashboard
                }
                return true;
            //If clicked in the lighting checkbox
            case R.id.lighting_1:
                lrl = (LinearLayout) findViewById(R.id.rl_lux);     //Get the lighting square id in the dashboard
                if(item.isChecked()) {  //If checkbox is already checked
                    item.setChecked(false); //Uncheck it
                    lrl.setVisibility(View.GONE);   //Make lighting square in the dashboard disappear
                    MenuItem it = menu.findItem(R.id.all);
                    it.setChecked(false);
                }
                //If it is not checked
                else {
                    item.setChecked(true);  //Check it
                    lrl.setVisibility(View.VISIBLE);    //Make lighting square appear in the dashboard
                }
                break;
            //If clicked in the noise checkbox
            case R.id.noise_1:
                RelativeLayout brl = (RelativeLayout) findViewById(R.id.rl_noise);      //Get the noise square id in the dashboard
                if(item.isChecked()) {  //If checkbox is already checked
                    item.setChecked(false); //Uncheck it
                    brl.setVisibility(View.GONE);   //Make noise square in the dashboard disappear
                    MenuItem it = menu.findItem(R.id.all);
                    it.setChecked(false);
                }
                //If it is not checked
                else {
                    item.setChecked(true);  //Check it
                    brl.setVisibility(View.VISIBLE);    //Make noise square appear in the dashboard
                }
                break;
            //If clicked in the UV radiation checkbox
            case R.id.radiation_1:
                brl = (RelativeLayout) findViewById(R.id.rl_uv);    //Get the UV square id in the dashboard
                if(item.isChecked()) {    //If checkbox is already checked
                    item.setChecked(false); //Uncheck it
                    brl.setVisibility(View.GONE);   //Make UV square in the dashboard disappear
                    MenuItem it = menu.findItem(R.id.all);
                    it.setChecked(false);
                }
                //If it is not checked
                else {
                    item.setChecked(true);  //Check it
                    brl.setVisibility(View.VISIBLE);    //Make UV square appear in the dashboard
                }
                break;
            //If clicked in the air checkbox
            case R.id.air_1:
                brl = (RelativeLayout) findViewById(R.id.rl_air);    //Get the air square id in the dashboard
                if(item.isChecked()) {    //If checkbox is already checked
                    item.setChecked(false); //Uncheck it
                    brl.setVisibility(View.GONE);   //Make air square in the dashboard disappear
                    MenuItem it = menu.findItem(R.id.all);
                    it.setChecked(false);
                }
                //If it is not checked
                else {
                    item.setChecked(true);  //Check it
                    brl.setVisibility(View.VISIBLE);    //Make air square appear in the dashboard
                }
                break;
            //If clicked in the waste checkbox
            case R.id.waste_1:
                brl = (RelativeLayout) findViewById(R.id.rl_waste);    //Get the waste square id in the dashboard
                if(item.isChecked()) {    //If checkbox is already checked
                    item.setChecked(false); //Uncheck it
                    brl.setVisibility(View.GONE);   //Make waste square in the dashboard disappear
                    MenuItem it = menu.findItem(R.id.all);
                    it.setChecked(false);
                }
                //If it is not checked
                else {
                    item.setChecked(true);  //Check it
                    brl.setVisibility(View.VISIBLE);    //Make waste square appear in the dashboard
                }
                break;
            //If clicked in the people checkbox
            case R.id.people_1:
                brl = (RelativeLayout) findViewById(R.id.rl_people);    //Get the people square id in the dashboard
                if(item.isChecked()) {    //If checkbox is already checked
                    item.setChecked(false); //Uncheck it
                    brl.setVisibility(View.GONE);   //Make people square in the dashboard disappear
                    MenuItem it = menu.findItem(R.id.all);
                    it.setChecked(false);
                }
                //If it is not checked
                else {
                    item.setChecked(true);  //Check it
                    brl.setVisibility(View.VISIBLE);    //Make people square appear in the dashboard
                }
                break;
            //If clicked in the "All visible" checkbox
            case R.id.all:
                RelativeLayout br1 = (RelativeLayout) findViewById(R.id.rl_people);    //Get the temperature square id in the dashboard
                LinearLayout br2 = (LinearLayout) findViewById(R.id.rl_temp);    //Get the lighting square id in the dashboard
                LinearLayout br3 = (LinearLayout) findViewById(R.id.rl_lux);    //Get the noise square id in the dashboard
                RelativeLayout br4 = (RelativeLayout) findViewById(R.id.rl_noise);    //Get the UV square id in the dashboard
                RelativeLayout br5 = (RelativeLayout) findViewById(R.id.rl_waste);    //Get the air square id in the dashboard
                RelativeLayout br6 = (RelativeLayout) findViewById(R.id.rl_uv);    //Get the waste square id in the dashboard
                RelativeLayout br7 = (RelativeLayout) findViewById(R.id.rl_air);    //Get the people square id in the dashboard
                if(item.isChecked()) {    //If checkbox is already checked
                    item.setChecked(true); //keep it checked
                    Context context = getApplicationContext();
                    Toast toast = Toast.makeText(context, "All metrics are already visible", Toast.LENGTH_SHORT);
                    toast.show();
                    System.out.println("Item is: "+item);
                }
                //If it is not checked
                else {
                    item.setChecked(true);  //Check it
                    br1.setVisibility(View.VISIBLE);    //Make temperature square appear in the dashboard
                    br2.setVisibility(View.VISIBLE);    //Make lighting square appear in the dashboard
                    br3.setVisibility(View.VISIBLE);    //Make noise square appear in the dashboard
                    br4.setVisibility(View.VISIBLE);    //Make UV square appear in the dashboard
                    br5.setVisibility(View.VISIBLE);    //Make air square appear in the dashboard
                    br6.setVisibility(View.VISIBLE);    //Make waste square appear in the dashboard
                    br7.setVisibility(View.VISIBLE);    //Make people square appear in the dashboard

                    System.out.println("menu: "+menu);

                    MenuItem it = menu.findItem(R.id.temperature_1);
                    it.setChecked(true);
                    it = menu.findItem(R.id.lighting_1);
                    it.setChecked(true);
                    it = menu.findItem(R.id.noise_1);
                    it.setChecked(true);
                    it = menu.findItem(R.id.radiation_1);
                    it.setChecked(true);
                    it = menu.findItem(R.id.air_1);
                    it.setChecked(true);
                    it = menu.findItem(R.id.waste_1);
                    it.setChecked(true);
                    it = menu.findItem(R.id.people_1);
                    it.setChecked(true);
                }
                break;
            default:
                return super.onOptionsItemSelected(item);
        }
        return true;
    }

    @Override
    public boolean onNavigationItemSelected(@NonNull MenuItem item) {
        // Handle navigation view item clicks here.
        int id = item.getItemId();  //get the id of the item clicked
        Intent intent;
        switch (id) {
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
            //If clicked on the alerts item
            case R.id.alerts:
                intent = new Intent(this, AlertsActivity.class);
                startActivity(intent);   //Launch alerts activity
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

    // Make dashboard tiles clickable
    public void changeToTemperature(View view) {
        Intent intent = new Intent(this, Temperature.class);
        startActivity(intent);
    }
    public void changeToLighting(View view) {
        Intent intent = new Intent(this, Lighting.class);
        startActivity(intent);
    }
    public void changeToUV(View view) {
        Intent intent = new Intent(this, UV_Radiation.class);
        startActivity(intent);
    }
    public void changeToWaste(View view) {
        Intent intent = new Intent(this, Waste.class);
        startActivity(intent);
    }
    public void changeToNoise(View view) {
        Intent intent = new Intent(this, Noise.class);
        startActivity(intent);
    }
    public void changeToPeople(View view) {
        Intent intent = new Intent(this, People.class);
        startActivity(intent);
    }
    public void changeToAir(View view) {
        Intent intent = new Intent(this, Air.class);
        startActivity(intent);
    }

    // Gps methods
    @Override
    public void onConnected(Bundle bundle) {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.M) {
            if (checkSelfPermission(android.Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
                Log.d(TAG, "No GPS permission");
                    requestPermissions(new String[] {
                                Manifest.permission.ACCESS_FINE_LOCATION
                            }, 10);
                    return;
            }
        }
        // If there is no previous location fetch last known one
        if (mCurrentLocation == null) {
            Log.d(TAG, "No previous location");
            mCurrentLocation = LocationServices.FusedLocationApi.getLastLocation(mGoogleApiClient);
            if(mCurrentLocation != null) Log.d(TAG, mCurrentLocation.toString());
        }
        // Start listening to location changes if not doing so already
        if(!listeningToChanges) {
            Log.d(TAG, "Started listening to location changes");
            requestLocationUpdates();
        }
        // Launch async task (populating dashboard) if we have a location
        if(mCurrentLocation != null) {
            new PopulateMainMetrics().execute();
            Log.d(TAG, "Launching new async task after connecting");
        }
    }

    @Override
    public void onConnectionSuspended(int i) {

    }

    @Override
    public void onConnectionFailed(@NonNull ConnectionResult connectionResult) {

    }

    @Override
    public void onLocationChanged(Location location) {
        mCurrentLocation = location;
        Log.d(TAG, "New lat "+location.getLatitude() +" lon " + location.getLongitude());
        Log.d(TAG, "Location changed, launching new async task");
        // When location changes fetch new data
        new PopulateMainMetrics().execute();
    }

    private void requestLocationUpdates() {
        // Start listening to location changes
        if (ActivityCompat.checkSelfPermission(this, android.Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED && ActivityCompat.checkSelfPermission(this, android.Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            Intent intent = new Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS);
            startActivity(intent);
            return;
        }
        LocationServices.FusedLocationApi.requestLocationUpdates(mGoogleApiClient, locationRequest, this);
        listeningToChanges = true;
    }

    private void stopLocationUpdates() {
        // Stop listening to location changes
        LocationServices.FusedLocationApi.removeLocationUpdates(mGoogleApiClient, this);
        listeningToChanges = false;
    }

    // Async task populate dashboard
    private class PopulateMainMetrics extends AsyncTask<Void, Void, Void> {
        private JSONObject json_response = null;
        private String url = "http://178.62.255.129/mobile/dashboard/"+mCurrentLocation.getLatitude()+"/"+mCurrentLocation.getLongitude();  // Test url

        TextView temp_tv = (TextView) findViewById(R.id.temperature_value_text);
        TextView light_tv = (TextView) findViewById(R.id.lightng_value_text);
        TextView uv_tv = (TextView) findViewById(R.id.uv_value_text);
        TextView waste_tv = (TextView) findViewById(R.id.waste_value_text);
        TextView noise_tv = (TextView) findViewById(R.id.noise_value_text);
        TextView people_tv = (TextView) findViewById(R.id.people_value_text);
        TextView air_tv = (TextView) findViewById(R.id.air_value_text);
        ProgressBar waste_pb = (ProgressBar) findViewById(R.id.progressBarWaste);
        ProgressBar light_pb = (ProgressBar) findViewById(R.id.progressBarLight);
        ProgressBar people_pb = (ProgressBar) findViewById(R.id.progressBarPeople);

        @Override
        protected void onPreExecute() {
            // Set all text to loading
            super.onPreExecute();
            temp_tv.setText(R.string.loading_temp);
            light_tv.setText(R.string.loading_light);
            uv_tv.setText(R.string.loading_uv);
            waste_tv.setText(R.string.loading_waste);
            noise_tv.setText(R.string.loading_noise);
            people_tv.setText(R.string.loading_people);
            air_tv.setText(R.string.loading_air);
            waste_pb.setVisibility(ProgressBar.INVISIBLE);
            people_pb.setVisibility(ProgressBar.INVISIBLE);
            light_pb.setVisibility(ProgressBar.INVISIBLE);
        }
        @Override
        protected Void doInBackground(Void... params) {
            // Get dashboard data
            try {
                URL url = new URL(this.url);
                HttpURLConnection httpURLConnection = (HttpURLConnection) url.openConnection();
                httpURLConnection.setConnectTimeout(5000);
                InputStream input = httpURLConnection.getInputStream();
                BufferedReader reader = new BufferedReader(new InputStreamReader(input));
                StringBuilder sb = new StringBuilder();
                String line;
                while((line = reader.readLine()) != null) {
                    sb.append(line);
                }
                json_response = new JSONObject(sb.toString());
                reader.close();
                input.close();
                httpURLConnection.disconnect();
            } catch (Exception e) {
                e.printStackTrace();
            }
            return null;
        }
        @Override
        protected void onPostExecute(Void avoid) {
            // If no response set error message
            if (json_response == null) {
                Log.d(TAG, "No response found");
                temp_tv.setText(R.string.server_error);
                light_tv.setText(R.string.server_error);
                uv_tv.setText(R.string.server_error);
                waste_tv.setText(R.string.server_error);
                noise_tv.setText(R.string.server_error);
                people_tv.setText(R.string.server_error);
            } else {
                // If we have a response show it on the dashboard
                try {
                    // Temperature
                    JSONObject temperature = json_response.getJSONObject("temperature");
                    String temp_status = temperature.get("status").toString();
                    // check if ok
                    if (temp_status.equals("OK")) {
                        Double temp_val = temperature.getDouble("value");
                        temp_tv.setText(String.format("%.2f ºC", temp_val));

                    } else {
                        // display error info
                        temp_tv.setText(temperature.get("info").toString());
                    }

                    // Lighting
                    JSONObject lighting = json_response.getJSONObject("light");
                    String light_status = lighting.get("status").toString();
                    // check if ok
                    if (light_status.equals("OK")) {
                        int light_val = lighting.getInt("value");
                        light_tv.setText(String.format("%d", light_val)+ " %");
                        light_pb.setVisibility(ProgressBar.VISIBLE);
                        light_pb.setProgress(light_val);

                    } else {
                        // display error info
                        light_tv.setText(lighting.get("info").toString());
                    }

                    // UV Radiation
                    JSONObject uv = json_response.getJSONObject("uv");
                    String uv_status = uv.get("status").toString();
                    // check if ok
                    if (uv_status.equals("OK")) {
                        int uv_val = uv.getInt("value");
                        uv_tv.setText(String.format("%d", uv_val));

                    } else {
                        uv_tv.setText(uv.get("info").toString());
                    }

                    // Waste
                    JSONObject waste = json_response.getJSONObject("waste");
                    String waste_status = waste.get("status").toString();
                    // check if ok
                    if (waste_status.equals("OK")) {
                        int waste_val = waste.getInt("value");
                        waste_tv.setText(String.format("%d", waste_val)+ " %");
                        waste_pb.setVisibility(ProgressBar.VISIBLE);
                        waste_pb.setProgress(waste_val);

                    } else {
                        // display error info
                        waste_tv.setText(waste.get("info").toString());
                    }

                    // Noise
                    JSONObject noise = json_response.getJSONObject("sound");
                    String noise_status = noise.get("status").toString();
                    // check if ok
                    if (noise_status.equals("OK")) {
                        int noise_val = noise.getInt("value");
                        noise_tv.setText(String.format("%d dB", noise_val));

                    } else {
                        // display error info
                        noise_tv.setText(noise.get("info").toString());
                    }

                    // People
                    JSONObject people = json_response.getJSONObject("people");
                    String people_status = people.get("status").toString();
                    // check if ok
                    if (people_status.equals("OK")) {
                        int people_val = people.getInt("value");
                        people_tv.setText(String.format("%d", people_val)+ " %");
                        people_pb.setVisibility(ProgressBar.VISIBLE);
                        people_pb.setProgress(people_val);

                    } else {
                        // display error info
                        people_tv.setText(people.get("info").toString());
                    }

                    // Air
                    JSONObject air = json_response.getJSONObject("co2");
                    String air_status = air.get("status").toString();
                    // check if ok
                    if (air_status.equals("OK")) {
                        int air_val = air.getInt("value");
                        air_tv.setText(String.format("%d ppm", air_val));
                    } else {
                        // display error info
                        air_tv.setText(air.get("info").toString());
                    }
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }
        }
    }
}