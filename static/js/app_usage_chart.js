function renderTotalAppTime(period) {
  fetch("/get_usage_data", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chart_type: "apps_usage", period: period })
  })
    .then(response => response.json())
    .then(function (rows) {

      const colors = rows.map(row => row["Color"]); // генеруємо кольори для кожного імені
      const formatedTimes = rows.map(row => row["Duration(sec)"]).map(secondsToDhms); // форматую час для анотацій
      const fullNames = rows.map(row => row["Program"]);
      const customdata = rows.map((_, i) => [formatedTimes[i], fullNames[i]]);

      const x = rows.map(row => row["Duration(sec)"]);
      const y = rows.map(row => row["ShortName"]);

      const data = [{
        x: x,
        y: y,
        customdata: customdata,
        type: "bar",
        orientation: "h",
        marker: { color: colors },
        hovertemplate:
          '<b>%{customdata[0]}</b><extra></extra><br>' +
          '<i>%{customdata[1]}</i>'
      }];

      const first_words = {
        'today': rows[0]?.WeekDay || '',
        'week': 'За Тиждень',
        'month': 'За Місяць',
        'all_time': 'За весь час'
      }

      var dateRegexp = /^\d{4}-\d{2}-\d{2}$/
      let title_text = ''
      if (rows.length === 0) {
        title_text = 'Даних немає';
      } else if (dateRegexp.test(period)) {
        title_text = rows[0]["WeekDay"] + " " + rows[0]["Date"]
      } else {
        title_text = first_words[String(period)] + " " + rows[0]["Date"]
      }
      const layout = {
        title: {
          text: title_text,
          font: {
            size: 22
          }
        },
        xaxis: { visible: false },
        yaxis: { automargin: true },
        font: {
          family: "Fantasy",
          weight: 100,
          color: "#EEEEEE"
        },
        annotations: { font: { family: "Nonito" } },
        margin: { t: 35, b: 20, l: 0, r: 0 },
        barcornerradius: '70%',
        paper_bgcolor: "#000000",
        plot_bgcolor: "#000000"
      };

      const config = {
        displayModeBar: false // 👈 Вимикає панель інструментів
      };

      Plotly.newPlot("appUsage", data, layout, config);
    })
};