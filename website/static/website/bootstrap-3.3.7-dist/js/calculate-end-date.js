/* 
code copied and modified from https://github.com/creios/angular-german-holidays
*/

function easterCalculationForYear(year) {
    // The date of Easter is computed by an algorithm found in the book of Meeus,
    // which is valid without exceptions for all years in the Gregorian Calendar
    // (from the year 1583 on)  Input: Year
    var a = year % 19;
    var b = Math.floor(year / 100);
    var c = year % 100;
    var d = Math.floor(b / 4);
    var e = b % 4;
    var f = Math.floor((b + 8) / 25);
    var g = Math.floor((b - f + 1) / 3);
    var h = (19 * a + b - d - g + 15) % 30;
    var i = Math.floor(c / 4);
    var k = c % 4;
    var l = (32 + 2 * e + 2 * i - h - k) % 7;
    var m = Math.floor((a + 11 * h + 22 * l) / 451);
    var n = Math.floor((h + l - 7 * m + 114) / 31);
    var p = (h + l - 7 * m + 114) % 31;
    p = Math.round(p + 1);
    return new Date(year, n - 1, p);
}

function holidayDefinitionsForYear(year) {
    var easter = easterCalculationForYear(year);
    
    function easterDependentDate(offset) {
        var date = new Date(easter.valueOf());
        date.setDate(easter.getDate() + offset);
        return date;
    }

    // dates based on https://de.wikipedia.org/wiki/Gesetzliche_Feiertage_in_Deutschland#.C3.9Cbersicht_aller_gesetzlichen_Feiertage
    return [
        {
            // Neujahrstag
            date: new Date(year, 0, 1),
        },
        {
            // Heilige drei Könige
            date: new Date(year, 0, 6),
        },
        {
            // Karfreitag
            date: easterDependentDate(-2),
        },
        {
            // Ostermontag
            date: easterDependentDate(+1),
        },
        {
            // Tag der Arbeit
            date: new Date(year, 4, 1),
        },
        {
            // Christi Himmelfahrt
            date: easterDependentDate(+39),
        },
        {
            // Pfingstmontag
            date: easterDependentDate(+50),
        },
        {
            // Fronleichnam
            date: easterDependentDate(+60),
        },
        {
            // Tag der deutschen Einheit
            date: new Date(year, 9, 3),
        },
        {
            // Allerheiligen
            date: new Date(year, 10, 1),
        },
        {
            // 1. Weihnachtsfeiertag
            date: new Date(year, 11, 25),
        },
        {
            // 2. Weihnachtsfeiertag
            date: new Date(year, 11, 26),
        }
    ]
}
    
function holidayNameForDate(date) {
    var holidayDefinitions = holidayDefinitionsForYear(date.getFullYear());

    for (var i = 0; i < holidayDefinitions.length; i++) {
        if (holidayDefinitions[i].date.valueOf() == date.valueOf()) {
            return holidayDefinitions[i];
        }
    }

    return null;
}

function isHolidayForDate(date) {
    return holidayNameForDate(date) !== null;
}

function calculateDueDate(months) {
    let begin_day = document.getElementById("id_begin_date_day").value;
    let begin_month = document.getElementById("id_begin_date_month").value;
    let begin_year = document.getElementById("id_begin_date_year").value;

    if (parseInt(begin_month) + months > 11) { // > 11 since JS Date-months range form 0-11
        begin_year = parseInt(begin_year) + 1;
    }

    begin_month = (parseInt(begin_month) + months) % 12;
    let due_date = new Date(begin_year, begin_month, begin_day);

    while (due_date.getDay() === 6 || due_date.getDay() === 0 || isHolidayForDate(due_date)) {
        due_date.setDate(due_date.getDate() + 1);
    }

    document.getElementById("id_due_date_day").value = due_date.getDate();
    document.getElementById("id_due_date_month").value = due_date.getMonth() + 1;
    document.getElementById("id_due_date_year").value = due_date.getFullYear();
}

function calculateProlongationDate() {
    let due_date = document.getElementById("id_due_date").value;
    let year = due_date.split("-")[0];
    let month = due_date.split("-")[1];
    let day = due_date.split("-")[2];

    let prolong_date = new Date(parseInt(year), month - 1, parseInt(day));
    let weeks = document.getElementById("id_weeks").value;
    prolong_date.setDate(prolong_date.getDate() + weeks * 7);

    while (prolong_date.getDay() === 6 || prolong_date.getDay() === 0 || isHolidayForDate(prolong_date)) {
        prolong_date.setDate(prolong_date.getDate() + 1);
    }

    document.getElementById("id_prolongation_date_day").value = prolong_date.getDate();
    document.getElementById("id_prolongation_date_month").value = prolong_date.getMonth() + 1;
    document.getElementById("id_prolongation_date_year").value = prolong_date.getFullYear();
}