function renderTimeTable(period) {
    fetch("/get_usage_data", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ chart_type: "time_table", period: period })
    })
        .then(response => response.json())
        .then(function (rows) {
            var dateRegexp = /^\d{4}-\d{2}-\d{2}$/

            function timeToSeconds(timeStr) {
                const [h, m, s] = timeStr.split(":").map(Number);
                return h * 3600 + m * 60 + s;
            }
            function dateTimeToSec(date, time) {
                var dateTime = new Date(String(date + ' ' + time))
                return dateTime.getTime() / 1000;
            }
            const data = rows.map(row => ({
                type: 'bar',
                orientation: 'h',
                x: [row['Duration(sec)']],
                y: [row['ShortName']],
                base: period === 'today' || dateRegexp.test(period) ? timeToSeconds(row['StartTime']) : dateTimeToSec(row['Date'], row['StartTime']),
                marker: { color: row['Color'] },
                hovertemplate: `<b>${row['Program']}</b><br><i>Початок: ${row['StartTime']}<br>Тривалість: ${secondsToDhms(row['Duration(sec)'])}<br>Вього за період: ${secondsToDhms(row['TotalDuration(sec)'])}</i><extra></extra>`
            }));

            function toDateTime(secs) {
                var t = new Date(1970, 0, 1); // Epoch
                t.setSeconds(secs);
                return t;
            };

            const first_words = {
                'week': 'За Тиждень',
                'month': 'За Місяць',
                'all_time': 'За весь час',
            };
            const clearance = 0.01;
            let title_text = '';

            if (rows.length === 0) {
                title_text = 'Даних немає';
            }
            else if (period == 'today' || dateRegexp.test(period)) {
                title_text = rows[0]["WeekDay"] + " " + rows[0]["Date"]
                let minTime = Math.min(...rows.map(row => timeToSeconds(row['StartTime'])));
                let maxTime = Math.max(...rows.map(row => timeToSeconds(row['StartTime']) + row['Duration(sec)']));
                minTime = minTime - ((maxTime - minTime) * clearance);
                maxTime = maxTime + ((maxTime - minTime) * clearance);
                layout_xaxis = {
                    range: [minTime, maxTime],
                    tickvals: [...Array(25).keys()].map(h => h * 3600),
                    ticktext: [...Array(25).keys()].map(h => `${h.toString().padStart(2, "0")}:00`),
                    tickangle: -45,
                    gridcolor: '#333333',
                    griddash: 'dot'
                }
            } else {
                // const dayTimeName = ['ніч', 'ранок', 'день', 'вечір']
                const dayTimeSeconds = ['00:00', '06:00', '12:00', '18:00']
                const unique = [...new Set(rows.map(row => row['Date']))];
                let timeline_names = []
                let timeline = []
                unique.forEach(d => {
                    dayTimeSeconds.forEach(dt => timeline.push(dateTimeToSec(d, dt)))
                    dayTimeSeconds.forEach(dtn => timeline_names.push(d + ' ' + dtn))
                })
                timeline.sort((a, b) => a - b)
                timeline_names.sort((a, b) => ('' + a).localeCompare(b))
                let minTime = Math.min(...rows.map(row => dateTimeToSec(row['Date'], row['StartTime'])));
                let maxTime = Math.max(...rows.map(row => dateTimeToSec(row['Date'], row['StartTime']) + row['Duration(sec)']));
                minTime = minTime - ((maxTime - minTime) * clearance);
                maxTime = maxTime + ((maxTime - minTime) * clearance);
                title_text = first_words[String(period)] + " " + toDateTime(minTime).toISOString().split('T')[0] + ' – ' + toDateTime(maxTime).toISOString().split('T')[0]

                layout_xaxis = {
                    range: [minTime, maxTime],
                    tickvals: [...timeline],
                    ticktext: [...timeline_names],
                    tickangle: -45,
                    gridcolor: '#333333',
                    griddash: 'dot'
                }
            }

            const layout = {
                title: {
                    text: title_text,// text: period === 'today' ? first_words[String(period)] + " " + rows[0]["Date"] : first_words[String(period)] + " " + rows[0]["Date"] + "-" + rows[-1]["Date"],
                    font: {
                        size: 22
                    }
                },
                barmode: 'stack',
                xaxis: layout_xaxis,
                yaxis: { automargin: true, },
                paper_bgcolor: "#000000",
                plot_bgcolor: "#000000",
                font: {
                    family: "Fantasy",
                    weight: 100,
                    color: "#EEEEEE"
                },
                annotations: { font: { family: "Nonito" } },
                margin: { t: 35, b: 75, l: 0, r: 0 },
                // barcornerradius: '1%',
                showlegend: false,
                height: 750,
            };

            const config = {
                displayModeBar: false // 👈 Вимикає панель інструментів
            };
            Plotly.newPlot('timeTable', data, layout, config);
        }).catch(error => console.error('Помилка при отриманні даних:', error));
};