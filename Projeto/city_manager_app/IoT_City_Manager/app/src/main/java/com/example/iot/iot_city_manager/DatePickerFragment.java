package com.example.iot.iot_city_manager;


import android.app.DatePickerDialog;
import android.app.Dialog;
import android.app.DialogFragment;
import android.os.Bundle;
import android.widget.DatePicker;

import java.util.Calendar;

public class DatePickerFragment extends DialogFragment implements DatePickerDialog.OnDateSetListener {

    private DatePickerDialog dialog;
    private long maxd, mind ;


    public DatePickerFragment (long minDate, long maxDate)
    {
        mind = minDate;
        maxd = maxDate;
    }


    @Override
    public Dialog onCreateDialog(Bundle savedInstanceState) {

        // Use the current date as the default date in the picker
        final Calendar c = Calendar.getInstance();
        int year = c.get(Calendar.YEAR);
        int month = c.get(Calendar.MONTH);
        int day = c.get(Calendar.DAY_OF_MONTH);

        // Create a new instance of DatePickerDialog and return it
        dialog = new DatePickerDialog(getActivity(),this, year, month, day);
        /*dialog.getDatePicker().setMaxDate(maxd);
        dialog.getDatePicker().setMinDate(mind);
        */
        dialog.getDatePicker().setMaxDate(maxd);
        dialog.getDatePicker().setMinDate(mind);

        return dialog;
    }

    public void onDateSet(DatePicker view, int year, int month, int day) {
        // Do something with the date chosen by the user
        //Waste.setDate(year, month, day);
    }
    public DatePickerDialog getMyDialog()
    {
        return dialog;
    }



}
