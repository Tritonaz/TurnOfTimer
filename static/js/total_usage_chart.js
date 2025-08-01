function renderTotalLine(period) {
  fetch("/get_usage_data", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ chart_type: "total_usage", period: period })
  })
    .then(response => response.json())
    .then(function (rows) {

      const colors = rows.map(row => row["Color"])
      let totalTime = 0
      rows.map(row => parseFloat(row["Duration(sec)"])).forEach(num => { totalTime += num });

      let x = rows.map(row => row['Duration(sec)'])
      let names = rows.map(row => row['BigApp'])
      const offset = totalTime * 0.2; // 20% від загального часу, можна змінити
      let base = offset;
      const data = x.map((val, i) => {
        const bar = {
          x: [val],
          y: ["Total Duration"],
          name: names[i],
          type: "bar",
          orientation: "h",
          marker: {
            color: colors[i],
            line: { width: 0 }
          },
          width: 1,
          text: names[i] + ' (' + Math.round(val / totalTime * 100) + '%)'
            + '<br>' + secondsToDhms(val),
          textposition: 'inside',
          hovertemplate: '<b>%{fullData.text}</b><extra></extra>'
        };
        bar.base = [base];
        base += val;
        return bar;
      });

      const layout = {
        colorway: colors,
        barmode: 'stack',
        showlegend: false,
        xaxis: { visible: false },
        yaxis: { automargin: true, visible: false },
        font: {
          family: "Fantasy",
          weight: 100,
          color: "#EEEEEE"
        },
        // width:
        height: 50,
        annotations: { font: { family: "Nonito" } },
        margin: { t: 0, b: 10, l: 0, r: 0 },
        barcornerradius: '15%',
        paper_bgcolor: "#000000",
        plot_bgcolor: "#000000"
      };

      const config = {
        displayModeBar: false
      };

      Plotly.newPlot('totalUsage', data, layout, config);
    }).catch(error => console.error('Помилка при отриманні даних:', error));
};
