package com.example.iot.iot_city;

import android.app.DialogFragment;
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
import android.widget.TableLayout;
import android.widget.TableRow;
import android.widget.TextView;

import com.jjoe64.graphview.DefaultLabelFormatter;
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
import java.util.Random;
import java.util.TimeZone;

public class Noise extends AppCompatActivity  implements NavigationView.OnNavigationItemSelectedListener {
    private DrawerLayout drawer;
    private ActionBarDrawerToggle toggle;
    long maxDate, minDate;
    String sensors_data[][];
    LineGraphSeries<DataPoint> series[];
    GraphView graph;
    StaticLabelsFormatter staticLabelsFormatter;
    int colors[] = {Color.BLUE, Color.RED, Color.GREEN, Color.GRAY , Color.YELLOW, Color.DKGRAY, Color.CYAN, Color.MAGENTA, Color.LTGRAY, Color.BLACK};

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_noise);
        Toolbar toolbar = (Toolbar) findViewById(R.id.toolbar);
        setSupportActionBar(toolbar);

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
        maxDate = new Date().getTime();
        Calendar c = Calendar.getInstance();
        c.add(Calendar.DAY_OF_MONTH, -3);
        minDate = c.getTimeInMillis();

        graphSetup();

        new PopulateData().execute();
    }

    private void graphSetup()
    {
        // Graph
        // http://www.android-graphview.org/dates-as-labels/

        graph = (GraphView) findViewById(R.id.graph);

        staticLabelsFormatter = new StaticLabelsFormatter(graph);

        // set manual Y bounds
        graph.getViewport().setYAxisBoundsManual(true);
        graph.getViewport().setMinY(0);
        graph.getViewport().setMaxY(100);

        // set manual X bounds
        graph.getViewport().setXAxisBoundsManual(false);
        setGraphLabels();

        // enable scaling and scrolling
        graph.getViewport().setScalable(false);
        graph.getViewport().setScalableY(false);

        graph.getViewport().setScrollable(false); // enables horizontal scrolling
        graph.getViewport().setScrollableY(true); // enables vertical scrolling

        graph.removeAllSeries();
    }

    private void setGraphLabels()
    {
        graph.getViewport().setMinX(minDate);
        graph.getViewport().setMaxX(maxDate);

        String begin, middle, end;
        Calendar c  = Calendar.getInstance();
        c.setTimeInMillis(minDate);
        begin = Integer.toString(c.get(Calendar.DAY_OF_MONTH)) + "/" + Integer.toString(c.get(Calendar.MONTH)+1) + "/" + Integer.toString(c.get(Calendar.YEAR)).substring(2);
        c.setTimeInMillis((maxDate+minDate)/2);
        middle = Integer.toString(c.get(Calendar.DAY_OF_MONTH)) + "/" + Integer.toString(c.get(Calendar.MONTH)+1) + "/" + Integer.toString(c.get(Calendar.YEAR)).substring(2);
        c.setTimeInMillis(maxDate);
        end = Integer.toString(c.get(Calendar.DAY_OF_MONTH)) + "/" + Integer.toString(c.get(Calendar.MONTH)+1) + "/" + Integer.toString(c.get(Calendar.YEAR)).substring(2);

        staticLabelsFormatter.setHorizontalLabels(new String[] {begin, middle, end});
        graph.getGridLabelRenderer().setLabelFormatter(staticLabelsFormatter);

    }

    private void dataSetup()
    {
        // Table
        // http://stackoverflow.com/questions/18049708/how-to-create-a-dynamic-table-of-data-in-android
        // http://stackoverflow.com/questions/2108456/how-can-i-create-a-table-with-borders-in-android
        TableLayout temp = (TableLayout) findViewById(R.id.noise_table);
        temp.setStretchAllColumns(true);
        temp.bringToFront();

        for (int i = 0; i < sensors_data.length; i++) {
            TableRow tr = new TableRow(this);
            tr.setBackgroundColor(Color.rgb(205, 205, 205));
            tr.setPadding(0, 0, 2, 2);

            TextView c1 = new TextView(this);
            c1.setBackgroundColor(Color.rgb(180, 180, 180));
            c1.setText(String.valueOf(sensors_data[i][0]));

            TextView c2 = new TextView(this);
            c2.setBackgroundColor(Color.rgb(180, 180, 180));
            c2.setText(String.valueOf(sensors_data[i][1]));

            TextView c3 = new TextView(this);
            c3.setBackgroundColor(Color.rgb(180, 180, 180));
            c3.setText(String.valueOf(sensors_data[i][2]));

            TextView c4 = new TextView(this);
            c4.setBackgroundColor(Color.rgb(180, 180, 180));
            c4.setText(String.valueOf(sensors_data[i][3]));

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
                        graph.addSeries(series[checkBox.getId()]);
                    }
                    else
                    {
                        graph.removeSeries(series[checkBox.getId()]);
                    }
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
                    data.putString("Sensor_id", sensors_data[x][0]);
                    Intent intent = new Intent(Noise.this, MapSensor.class);
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
            tr.addView(button);
            //tr.addView(c2);
            tr.addView(c3);
            tr.addView(c4);

            temp.addView(tr);
        }
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
            case R.id.begin_date:
                newFragment = new DatePickerFragment(min.getTimeInMillis(), maxDate) {
                    @Override
                    public void onDateSet(DatePicker view, int year, int month, int day) {
                        Calendar c = Calendar.getInstance();
                        c.set(year, month, day);
                        minDate = c.getTimeInMillis();
                        setGraphLabels();
                        // forces the graph to update
                        graph.addSeries(temp);
                        graph.removeSeries(temp);
                    }
                };
                newFragment.show(getFragmentManager(), "datePicker");
                break;
            case R.id.end_date:
                newFragment = new DatePickerFragment(minDate, new Date().getTime()) {
                    @Override
                    public void onDateSet(DatePicker view, int year, int month, int day) {
                        Calendar c = Calendar.getInstance();
                        c.set(year, month, day);
                        maxDate = c.getTimeInMillis();
                        setGraphLabels();
                        // forces the graph to update
                        graph.addSeries(temp);
                        graph.removeSeries(temp);
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
            case R.id.air:
                intent = new Intent(this, Air.class);
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
        private String url = "http://178.62.255.129/mobile/noise/";  // Test url // 192.168.1.129:8000 // 193.136.92.216:5010

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
                    JSONArray values = json_response.getJSONArray("values");   // all values
                    System.out.println("Temos dados de sensores!");
                    sensors_data= new String[sensors.length()][4];
                    series = new LineGraphSeries[values.length()];
                    // temperature format
                    DecimalFormat format = new DecimalFormat("#.#");

                    // run through all sensors
                    for(int i=0; i < sensors.length(); i++) {
                        JSONObject sensor = sensors.getJSONObject(i);
                        sensors_data[i][0] = sensor.getString("id");
                        sensors_data[i][1] = sensor.getString("address");

                        DataPoint[] dp = new DataPoint[0];
                        JSONArray temperatures = null;

                        // since all values are not in the same index as the corresponding sensors, we have to search for the values for each sensor
                        for (int j = 0; j < values.length() ; j++)
                        {
                            JSONObject temporary = values.getJSONObject(j);
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
                                        sensors_data[i][2] = dt.format(d);
                                        sensors_data[i][3] = format.format(temperatura);
                                    }
                                }
                                break;
                            } catch (Exception e) {
                            }
                        }
                        series[i] = new LineGraphSeries<>(dp);                         series[i].setColor(colors[i]);                   }
                    dataSetup();

                } catch (Exception e) {
                    e.printStackTrace();
                }
            }
        }
    }
}

