package com.example.iot.iot_city_manager;

import android.content.Intent;
import android.content.res.ColorStateList;
import android.graphics.Color;
import android.os.AsyncTask;
import android.os.Bundle;
import android.support.design.widget.NavigationView;
import android.support.v4.view.GravityCompat;
import android.support.v4.widget.DrawerLayout;
import android.support.v7.app.ActionBarDrawerToggle;
import android.support.v7.app.AppCompatActivity;
import android.support.v7.widget.Toolbar;
import android.view.Menu;
import android.view.MenuItem;
import android.view.View;
import android.widget.Button;
import android.widget.CheckBox;
import android.widget.CompoundButton;
import android.widget.DatePicker;
import android.widget.ImageButton;
import android.widget.TabHost;
import android.widget.TableLayout;
import android.widget.TableRow;
import android.widget.TextView;

import com.jjoe64.graphview.GraphView;
import com.jjoe64.graphview.helper.StaticLabelsFormatter;
import com.jjoe64.graphview.series.DataPoint;
import com.jjoe64.graphview.series.LineGraphSeries;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.DecimalFormat;
import java.text.SimpleDateFormat;
import java.util.Calendar;
import java.util.Date;
import java.util.TimeZone;

public class Air extends AppCompatActivity implements NavigationView.OnNavigationItemSelectedListener {
    private DrawerLayout drawer;
    private ActionBarDrawerToggle toggle;
    long maxDate[] = new long[2];
    long minDate[] = new long[2];
    String sensors_data[][][];
    LineGraphSeries<DataPoint> series[][];
    GraphView graph[] = new GraphView[2];
    StaticLabelsFormatter staticLabelsFormatter[] = new StaticLabelsFormatter[2];
    int colors[] = {Color.BLUE, Color.RED, Color.GREEN, Color.GRAY , Color.YELLOW, Color.DKGRAY, Color.CYAN, Color.MAGENTA, Color.LTGRAY, Color.BLACK};


    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_air);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

        createTabs();

        // Navigation drawer
        NavigationView navigationView = (NavigationView) findViewById(R.id.nav_view);
        navigationView.setNavigationItemSelectedListener(this);

        View decorView = getWindow().getDecorView();
        // Hide the status bar.
        int uiOptions = View.SYSTEM_UI_FLAG_VISIBLE;
        decorView.setSystemUiVisibility(uiOptions);


        drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        toggle = new ActionBarDrawerToggle(this, drawer,
                toolbar,
                R.string.navigation_drawer_open,
                R.string.navigation_drawer_close ) {
        };

        drawer.addDrawerListener(toggle);
        toggle.syncState();

        //default max and min date values
        maxDate[0]=  new Date().getTime();
        maxDate[1] = new Date().getTime();
        Calendar c = Calendar.getInstance();
        c.add(Calendar.DAY_OF_MONTH, -3);
        minDate[0] = c.getTimeInMillis();
        minDate[1] = c.getTimeInMillis();

        graphSetup();
        new PopulateData().execute();
    }

    private void graphSetup()
    {
        // Graph
        // http://www.android-graphview.org/dates-as-labels/

        graph[0] = (GraphView) findViewById(R.id.graph_co2);

        staticLabelsFormatter[0] = new StaticLabelsFormatter(graph[0]);

        // set manual Y bounds
        graph[0].getViewport().setYAxisBoundsManual(true);
        graph[0].getViewport().setMinY(0);
        graph[0].getViewport().setMaxY(30);

        // set manual X bounds
        graph[0].getViewport().setXAxisBoundsManual(false);

        // enable scaling and scrolling
        graph[0].getViewport().setScalable(false);
        graph[0].getViewport().setScalableY(false);

        graph[0].getViewport().setScrollable(false); // enables horizontal scrolling
        graph[0].getViewport().setScrollableY(true); // enables vertical scrolling

        graph[0].removeAllSeries();

        graph[1] = (GraphView) findViewById(R.id.graph_pressure);

        staticLabelsFormatter[1] = new StaticLabelsFormatter(graph[1]);

        // set manual Y bounds
        graph[1].getViewport().setYAxisBoundsManual(true);
        graph[1].getViewport().setMinY(1000);
        graph[1].getViewport().setMaxY(1100);

        // set manual X bounds
        graph[1].getViewport().setXAxisBoundsManual(false);

        // enable scaling and scrolling
        graph[1].getViewport().setScalable(false);
        graph[1].getViewport().setScalableY(false);

        graph[1].getViewport().setScrollable(false); // enables horizontal scrolling
        graph[1].getViewport().setScrollableY(true); // enables vertical scrolling

        graph[1].removeAllSeries();

        setGraphLabels();
    }

    private void setGraphLabels()
    {
        graph[0].getViewport().setMinX(minDate[0]);
        graph[0].getViewport().setMaxX(maxDate[0]);

        String begin, middle, end;
        Calendar c  = Calendar.getInstance();
        c.setTimeInMillis(minDate[0]);
        begin = Integer.toString(c.get(Calendar.DAY_OF_MONTH)) + "/" + Integer.toString(c.get(Calendar.MONTH)+1) + "/" + Integer.toString(c.get(Calendar.YEAR)).substring(2);
        c.setTimeInMillis((maxDate[0]+minDate[0])/2);
        middle = Integer.toString(c.get(Calendar.DAY_OF_MONTH)) + "/" + Integer.toString(c.get(Calendar.MONTH)+1) + "/" + Integer.toString(c.get(Calendar.YEAR)).substring(2);
        c.setTimeInMillis(maxDate[0]);
        end = Integer.toString(c.get(Calendar.DAY_OF_MONTH)) + "/" + Integer.toString(c.get(Calendar.MONTH)+1) + "/" + Integer.toString(c.get(Calendar.YEAR)).substring(2);

        staticLabelsFormatter[0].setHorizontalLabels(new String[] {begin, middle, end});
        graph[0].getGridLabelRenderer().setLabelFormatter(staticLabelsFormatter[0]);

        graph[1].getViewport().setMinX(minDate[1]);
        graph[1].getViewport().setMaxX(maxDate[1]);

        c.setTimeInMillis(minDate[1]);
        begin = Integer.toString(c.get(Calendar.DAY_OF_MONTH)) + "/" + Integer.toString(c.get(Calendar.MONTH)+1) + "/" + Integer.toString(c.get(Calendar.YEAR)).substring(2);
        c.setTimeInMillis((maxDate[1]+minDate[1])/2);
        middle = Integer.toString(c.get(Calendar.DAY_OF_MONTH)) + "/" + Integer.toString(c.get(Calendar.MONTH)+1) + "/" + Integer.toString(c.get(Calendar.YEAR)).substring(2);
        c.setTimeInMillis(maxDate[1]);
        end = Integer.toString(c.get(Calendar.DAY_OF_MONTH)) + "/" + Integer.toString(c.get(Calendar.MONTH)+1) + "/" + Integer.toString(c.get(Calendar.YEAR)).substring(2);

        staticLabelsFormatter[1].setHorizontalLabels(new String[] {begin, middle, end});
        graph[1].getGridLabelRenderer().setLabelFormatter(staticLabelsFormatter[1]);

    }

    private void dataSetup()
    {
        // Table
        // http://stackoverflow.com/questions/18049708/how-to-create-a-dynamic-table-of-data-in-android
        // http://stackoverflow.com/questions/2108456/how-can-i-create-a-table-with-borders-in-android
        TableLayout table_co2 = (TableLayout) findViewById(R.id.air_table_co2);
        table_co2.setStretchAllColumns(true);
        table_co2.bringToFront();

        for (int i = 0; i < sensors_data[0].length; i++) {
            TableRow tr = new TableRow(this);
            tr.setBackgroundColor(Color.rgb(205, 205, 205));
            tr.setPadding(0, 0, 2, 2);

            TextView c1 = new TextView(this);
            c1.setBackgroundColor(Color.rgb(180, 180, 180));
            c1.setText(String.valueOf(sensors_data[0][i][0]));

            TextView c2 = new TextView(this);
            c2.setBackgroundColor(Color.rgb(180, 180, 180));
            c2.setText(String.valueOf(sensors_data[0][i][1]));

            TextView c3 = new TextView(this);
            c3.setBackgroundColor(Color.rgb(180, 180, 180));
            c3.setText(String.valueOf(sensors_data[0][i][2]));

            TextView c4 = new TextView(this);
            c4.setBackgroundColor(Color.rgb(180, 180, 180));
            c4.setText(String.valueOf(sensors_data[0][i][3]));

            final CheckBox checkBox = new CheckBox(getApplicationContext());
            checkBox.setBackgroundColor(Color.rgb(180, 180, 180));
            checkBox.setId(i);
            if(i < 10)
                checkBox.setButtonTintList(ColorStateList.valueOf(colors[i]));
            checkBox.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {

                @Override
                public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                    // TODO Auto-generated method stub
                    if(isChecked)
                    {
                        graph[0].addSeries(series[0][checkBox.getId()]);
                    }
                    else
                    {
                        graph[0].removeSeries(series[0][checkBox.getId()]);
                    }
                    graph[0].getViewport().setMinX(minDate[0]);
                    graph[0].getViewport().setMaxX(maxDate[0]);
                    System.out.println("carreguei na checkbox " + checkBox.getId());
                }
            });

            // location button
            final ImageButton button = new ImageButton(getApplicationContext());
            button.setBackgroundColor(Color.rgb(180, 180, 180));
            button.setId(1000+i);
            button.setImageResource(R.drawable.ic_place_black_24dp);
            final int x = i;
            button.setOnClickListener(new Button.OnClickListener(){
                public void onClick(View v) {
                    System.out.println("carreguei no botão " + button.getId());
                    Bundle data = new Bundle();
                    data.putString("Sensor_id", sensors_data[0][x][0]);
                    Intent intent = new Intent(Air.this, MapSensor.class);
                    intent.putExtras(data);
                    startActivityForResult(intent, 1);
                }
            });

            TableRow.LayoutParams params = new TableRow.LayoutParams(0, Toolbar.LayoutParams.MATCH_PARENT);
            params.setMargins(0,0,2,0);
            c1.setLayoutParams(params);
            //c2.setLayoutParams(params);
            button.setLayoutParams(params);
            checkBox.setLayoutParams(params);
            c4.setLayoutParams(params);
            c3.setLayoutParams(params);

            tr.addView(c1);
            tr.addView(checkBox);
            //tr.addView(c2);
            tr.addView(button);
            tr.addView(c3);
            tr.addView(c4);

            table_co2.addView(tr);
        }

        TableLayout table_pressure = (TableLayout) findViewById(R.id.air_table_pressure);
        table_pressure.setStretchAllColumns(true);
        table_pressure.bringToFront();

        for (int i = 0; i < sensors_data[0].length; i++) {
            TableRow tr = new TableRow(this);
            tr.setBackgroundColor(Color.rgb(205, 205, 205));
            tr.setPadding(0, 0, 2, 2);

            TextView c1 = new TextView(this);
            c1.setBackgroundColor(Color.rgb(180, 180, 180));
            c1.setText(String.valueOf(sensors_data[1][i][0]));

            TextView c2 = new TextView(this);
            c2.setBackgroundColor(Color.rgb(180, 180, 180));
            c2.setText(String.valueOf(sensors_data[1][i][1]));

            TextView c3 = new TextView(this);
            c3.setBackgroundColor(Color.rgb(180, 180, 180));
            c3.setText(String.valueOf(sensors_data[1][i][2]));

            TextView c4 = new TextView(this);
            c4.setBackgroundColor(Color.rgb(180, 180, 180));
            c4.setText(String.valueOf(sensors_data[1][i][3]));

            final CheckBox checkBox = new CheckBox(getApplicationContext());
            checkBox.setBackgroundColor(Color.rgb(180, 180, 180));
            checkBox.setId(i + 100);
            if(i < 10)
                checkBox.setButtonTintList(ColorStateList.valueOf(colors[i]));
            checkBox.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {

                @Override
                public void onCheckedChanged(CompoundButton buttonView, boolean isChecked) {
                    // TODO Auto-generated method stub
                    if(isChecked)
                    {
                        graph[1].addSeries(series[1][checkBox.getId()-100]);
                    }
                    else
                    {
                        graph[1].removeSeries(series[1][checkBox.getId()-100]);
                    }
                    graph[1].getViewport().setMinX(minDate[0]);
                    graph[1].getViewport().setMaxX(maxDate[0]);
                    System.out.println("carreguei na checkbox " + checkBox.getId());
                }
            });

            // location button
            final ImageButton button = new ImageButton(getApplicationContext());
            button.setBackgroundColor(Color.rgb(180, 180, 180));
            button.setId(1100+i);
            button.setImageResource(R.drawable.ic_place_black_24dp);

            button.setOnClickListener(new Button.OnClickListener(){
                public void onClick(View v) {
                    System.out.println("carreguei no botão " + button.getId());
                    //Do stuff here
                }
            });

            TableRow.LayoutParams params = new TableRow.LayoutParams(0, Toolbar.LayoutParams.MATCH_PARENT);
            params.setMargins(0,0,2,0);
            c1.setLayoutParams(params);
            c2.setLayoutParams(params);
            //button.setLayoutParams(params);
            checkBox.setLayoutParams(params);
            c4.setLayoutParams(params);
            c3.setLayoutParams(params);

            tr.addView(c1);
            tr.addView(checkBox);
            tr.addView(c2);
            //tr.addView(button);
            tr.addView(c3);
            tr.addView(c4);

            table_co2.addView(tr);
        }
    }

    private void createTabs()
    {
        // tabview
        TabHost host = (TabHost)findViewById(R.id.tabHost);
        host.setup();

        //Tab 1
        TabHost.TabSpec spec = host.newTabSpec("Tab One");
        spec.setContent(R.id.tab1);
        spec.setIndicator("CO2");
        host.addTab(spec);

        //Tab 2
        spec = host.newTabSpec("Tab Two");
        spec.setContent(R.id.tab2);
        spec.setIndicator("Pressure");
        host.addTab(spec);

    }

    // choose graph begin and end date
    public void showDatePickerDialog(View v)
    {
        Calendar min = Calendar.getInstance();
        min.set(2017, 0,1);
        DatePickerFragment newFragment;

        //min.setTimeInMillis(minDate);
        final LineGraphSeries<DataPoint> temp = new LineGraphSeries<>(new DataPoint[]{new DataPoint(0,0)});
        switch (v.getId())
        {
            case R.id.begin_date_co2:
                newFragment = new DatePickerFragment(min.getTimeInMillis(), maxDate[0]) {
                    @Override
                    public void onDateSet(DatePicker view, int year, int month, int day) {
                        Calendar c = Calendar.getInstance();
                        c.set(year, month, day);
                        minDate[0] = c.getTimeInMillis();
                        setGraphLabels();
                        // forces the graph to update
                        graph[0].addSeries(temp);
                        graph[0].removeSeries(temp);
                    }
                };
                newFragment.show(getFragmentManager(), "datePicker");
                break;
            case R.id.end_date_co2:
                newFragment = new DatePickerFragment(minDate[0], new Date().getTime()) {
                    @Override
                    public void onDateSet(DatePicker view, int year, int month, int day) {
                        Calendar c = Calendar.getInstance();
                        c.set(year, month, day);
                        maxDate[0] = c.getTimeInMillis();
                        setGraphLabels();
                        // forces the graph to update
                        graph[0].addSeries(temp);
                        graph[0].removeSeries(temp);
                    }
                };
                newFragment.show(getFragmentManager(), "datePicker");
                break;
            case R.id.begin_date_pressure:
                newFragment = new DatePickerFragment(min.getTimeInMillis(), maxDate[1]) {
                    @Override
                    public void onDateSet(DatePicker view, int year, int month, int day) {
                        Calendar c = Calendar.getInstance();
                        c.set(year, month, day);
                        minDate[1] = c.getTimeInMillis();
                        setGraphLabels();
                        // forces the graph to update
                        graph[1].addSeries(temp);
                        graph[1].removeSeries(temp);
                    }
                };
                newFragment.show(getFragmentManager(), "datePicker");
                break;
            case R.id.end_date_pressure:
                newFragment = new DatePickerFragment(minDate[1], new Date().getTime()) {
                    @Override
                    public void onDateSet(DatePicker view, int year, int month, int day) {
                        Calendar c = Calendar.getInstance();
                        c.set(year, month, day);
                        maxDate[1] = c.getTimeInMillis();
                        setGraphLabels();
                        // forces the graph to update
                        graph[1].addSeries(temp);
                        graph[1].removeSeries(temp);
                    }
                };
                newFragment.show(getFragmentManager(), "datePicker");
                break;
            default:
                break;
        }
    }


    @Override
    public boolean onCreateOptionsMenu(Menu menu) {
        return true;
    }

    @Override
    public boolean onOptionsItemSelected(MenuItem item) {
        // Handle action bar item clicks here. The action bar will
        // automatically handle clicks on the Home/Up button, so long
        // as you specify a parent activity in AndroidManifest.xml.
        return super.onOptionsItemSelected(item);
    }

    @Override
    public boolean onNavigationItemSelected(MenuItem item) {
        // Handle navigation view item clicks here.
        int id = item.getItemId();
        Intent intent;
        switch (id) {
            case R.id.nav_dashboard:
                intent = new Intent(this, MainActivity.class);
                startActivity(intent);
                break;
            case R.id.nav_map:
                intent = new Intent(this, MapsActivity.class);
                startActivity(intent);
                break;
            case R.id.temperature:
                intent = new Intent(this, Temperature.class);
                startActivity(intent);
                break;
            case R.id.lighting:
                intent = new Intent(this, Lighting.class);
                startActivity(intent);
                break;
            case R.id.radiation:
                intent = new Intent(this, UV_Radiation.class);
                startActivity(intent);
                break;
            case R.id.waste:
                intent = new Intent(this, Waste.class);
                startActivity(intent);
                break;
            case R.id.people:
                intent = new Intent(this, People.class);
                startActivity(intent);
                break;
            case R.id.help:
                intent = new Intent(this, Help.class);
                startActivity(intent);
                break;
            default:
                break;
        }
        DrawerLayout drawer = (DrawerLayout) findViewById(R.id.drawer_layout);
        drawer.closeDrawer(GravityCompat.START);
        return true;
    }

    // Async task populate
    class PopulateData extends AsyncTask<Void, Void, Void> {
        private JSONObject json_response = null;
        private String url = "http://178.62.255.129/mobile/air/";  // Test url // 192.168.1.129:8000 // 193.136.92.216:5010

        @Override
        protected void onPreExecute() {
            super.onPreExecute();

        }
        @Override
        protected Void doInBackground(Void... params) {
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
            if (json_response == null) {
                System.out.println("null json response");
            } else {
                try {
                    JSONArray sensors = json_response.getJSONArray("sensors"); // all sensors
                    JSONArray co2 = json_response.getJSONArray("co2"); // all values
                    JSONArray pressure = json_response.getJSONArray("pressure");
                    System.out.println("Temos dados de sensores!");
                    sensors_data= new String[2][sensors.length()][4];
                    series = new LineGraphSeries[2][sensors.length()];
                    // temperature format
                    DecimalFormat format = new DecimalFormat("#.#");

                    // run through all sensors
                    for(int i=0; i < sensors.length(); i++) {
                        JSONObject sensor = sensors.getJSONObject(i);
                        sensors_data[0][i][0] = sensor.getString("id");
                        sensors_data[0][i][1] = sensor.getString("address");
                        sensors_data[0][i][2] = " ";
                        sensors_data[0][i][3] = " ";
                        sensors_data[1][i][0] = sensor.getString("id");
                        sensors_data[1][i][1] = sensor.getString("address");
                        sensors_data[1][i][2] = " ";
                        sensors_data[1][i][3] = " ";

                        DataPoint[] dp = new DataPoint[0];
                        JSONArray temperatures = null;

                        // since all values are not in the same index as the corresponding sensors, we have to search for the values for each sensor
                        for (int j = 0; j < co2.length() ; j++)
                        {
                            JSONObject temporary = co2.getJSONObject(j);
                            try {
                                // if made correctly, we have a array of reading for sensor i
                                temperatures = temporary.getJSONArray(sensor.getJSONArray("streams").getString(0));
                                dp = new DataPoint[temperatures.length()];
                                // run through all readings into an array of data points(graph)
                                for (int k = 0; k < temperatures.length(); k++)
                                {
                                    JSONArray reading = temperatures.getJSONArray(k);
                                    double temperatura = reading.getDouble(1);
                                    JSONArray datetimestamp = reading.getJSONArray(0);
                                    Calendar c = Calendar.getInstance();
                                    c.setTimeZone(TimeZone.getTimeZone("GMT"));
                                    c.set(datetimestamp.getInt(0), datetimestamp.getInt(1)-1, datetimestamp.getInt(2), datetimestamp.getInt(3), datetimestamp.getInt(4));
                                    Date d = new Date();
                                    d.setTime(c.getTimeInMillis());
                                    dp[k] = new DataPoint(d, temperatura);
                                    if(k == temperatures.length()-1)
                                    {
                                        SimpleDateFormat dt = new SimpleDateFormat("dd/MM/yy hh:mm");
                                        sensors_data[0][i][2] = dt.format(d);
                                        sensors_data[0][i][3] = format.format(temperatura);
                                    }
                                }
                                break;
                            } catch (Exception e) {
                            }
                        }
                        series[0][i] = new LineGraphSeries<>(dp);
                        series[0][i].setColor(colors[i]);

                        // since all values are not in the same index as the corresponding sensors, we have to search for the values for each sensor
                        for (int j = 0; j < pressure.length() ; j++)
                        {
                            JSONObject temporary = pressure.getJSONObject(j);
                            try {
                                // if made correctly, we have a array of reading for sensor i
                                temperatures = temporary.getJSONArray(sensor.getJSONArray("streams").getString(0));
                                dp = new DataPoint[temperatures.length()];
                                // run through all readings into an array of data points(graph)
                                for (int k = 0; k < temperatures.length(); k++)
                                {
                                    JSONArray reading = temperatures.getJSONArray(k);
                                    double temperatura = reading.getDouble(1);
                                    JSONArray datetimestamp = reading.getJSONArray(0);
                                    Calendar c = Calendar.getInstance();
                                    c.setTimeZone(TimeZone.getTimeZone("GMT"));
                                    c.set(datetimestamp.getInt(0), datetimestamp.getInt(1)-1, datetimestamp.getInt(2), datetimestamp.getInt(3), datetimestamp.getInt(4));
                                    Date d = new Date();
                                    d.setTime(c.getTimeInMillis());
                                    dp[k] = new DataPoint(d, temperatura);
                                    if(k == temperatures.length()-1)
                                    {
                                        SimpleDateFormat dt = new SimpleDateFormat("dd/MM/yy hh:mm");
                                        sensors_data[1][i][2] = dt.format(d);
                                        sensors_data[1][i][3] = format.format(temperatura);
                                    }
                                }
                                break;
                            } catch (Exception e) {
                            }
                        }
                        series[1][i] = new LineGraphSeries<>(dp);
                        series[1][i].setColor(colors[i]);
                    }
                    dataSetup();

                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }
    }
}