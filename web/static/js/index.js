var start_date = null;
var end_date = null;

$('div#term input').change((eo) => {
    start_date = new Date($('div#term input.start-date').val());
    end_date = new Date($('div#term input.end-date').val());
    if(start_date.getTime() > end_date.getTime()){
        if(eo.currentTarget.className == "start-date"){
            end_date.setTime(start_date.getTime());
            $('div#term input.end-date').val(getDateStr(end_date));
        }else{
            start_date.setTime(end_date.getTime());
            $('div#term input.start-date').val(getDateStr(start_date));
        }
    }
});

function getDateStr(dateObj){
    var year = dateObj.getFullYear()
    var month = dateObj.getMonth() + 1
    if(month < 10){
        month = "0" + month
    }
    var date = dateObj.getDate()
    if(date < 10){
        date = "0" + date
    }

    return year + '-' + month + '-' + date
}