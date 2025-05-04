
$(function () {
    var data = [], totalPoints = 100
    function getRandomData() {
      if (data.length > 0) {
        data = data.slice(1)
      }
      // Do a random walk
      while (data.length < totalPoints) {
        var prev = data.length > 0 ? data[data.length - 1] : 50,
            y    = prev + Math.random() * 10 - 5
        if (y < 0) {
          y = 0
        } else if (y > 100) {
          y = 100
        }
        data.push(y)
      }

      // Zip the generated y values with the x values
      var res = []
      for (var i = 0; i < data.length; ++i) {
        res.push([i, data[i]])
      }

      return res
    }
    var interactive_plot = $.plot('#cpu', [
        {
          data: getRandomData(),
        }
      ],
      {
        grid: {
          borderColor: '#f3f3f3',
          borderWidth: 1,
          tickColor: '#f3f3f3'
        },
        series: {
          color: '#3c8dbc',
          lines: {
            lineWidth: 2,
            show: true,
            fill: true,
          },
        },
        yaxis: {
          min: 0,
          max: 100,
          show: true
        },
        xaxis: {
          show: true
        }
      }
    )
    var updateInterval = 500 //Fetch data ever x milliseconds
    var realtime       = 'on' //If == to on then fetch data every x seconds. else stop fetching
    function update() {

      interactive_plot.setData([getRandomData()])

      // Since the axes don't change, we don't need to call plot.setupGrid()
      interactive_plot.draw()
      if (realtime === 'on') {
        setTimeout(update, updateInterval)
      }
    }
    //INITIALIZE REALTIME DATA FETCHING
    if (realtime === 'on') {
      update()
    }
    //REALTIME TOGGLE
    $('#realtime .btn').click(function () {
      if ($(this).data('toggle') === 'on') {
        realtime = 'on'
      }
      else {
        realtime = 'off'
      }
      update()
    })
})

$(function () {
    var data = [], totalPoints = 100
    function getRandomData() {
      if (data.length > 0) {
        data = data.slice(1)
      }
      // Do a random walk
      while (data.length < totalPoints) {
        var prev = data.length > 0 ? data[data.length - 1] : 50,
            y    = prev + Math.random() * 10 - 5
        if (y < 0) {
          y = 0
        } else if (y > 100) {
          y = 100
        }
        data.push(y)
      }

      // Zip the generated y values with the x values
      var res = []
      for (var i = 0; i < data.length; ++i) {
        res.push([i, data[i]])
      }

      return res
    }
    var interactive_plot = $.plot('#ram', [
        {
          data: getRandomData(),
        }
      ],
      {
        grid: {
          borderColor: '#f3f3f3',
          borderWidth: 1,
          tickColor: '#f3f3f3'
        },
        series: {
          color: '#3c8dbc',
          lines: {
            lineWidth: 2,
            show: true,
            fill: true,
          },
        },
        yaxis: {
          min: 0,
          max: 100,
          show: true
        },
        xaxis: {
          show: true
        }
      }
    )
    var updateInterval = 500 //Fetch data ever x milliseconds
    var realtime       = 'on' //If == to on then fetch data every x seconds. else stop fetching
    function update() {

      interactive_plot.setData([getRandomData()])

      // Since the axes don't change, we don't need to call plot.setupGrid()
      interactive_plot.draw()
      if (realtime === 'on') {
        setTimeout(update, updateInterval)
      }
    }
    //INITIALIZE REALTIME DATA FETCHING
    if (realtime === 'on') {
      update()
    }
    //REALTIME TOGGLE
    $('#realtime .btn').click(function () {
      if ($(this).data('toggle') === 'on') {
        realtime = 'on'
      }
      else {
        realtime = 'off'
      }
      update()
    })
})
$(function () {
    var data = [], totalPoints = 100
    function getRandomData() {
      if (data.length > 0) {
        data = data.slice(1)
      }
      // Do a random walk
      while (data.length < totalPoints) {
        var prev = data.length > 0 ? data[data.length - 1] : 50,
            y    = prev + Math.random() * 10 - 5
        if (y < 0) {
          y = 0
        } else if (y > 100) {
          y = 100
        }
        data.push(y)
      }

      // Zip the generated y values with the x values
      var res = []
      for (var i = 0; i < data.length; ++i) {
        res.push([i, data[i]])
      }

      return res
    }
    var interactive_plot = $.plot('#gpu', [
        {
          data: getRandomData(),
        }
      ],
      {
        grid: {
          borderColor: '#f3f3f3',
          borderWidth: 1,
          tickColor: '#f3f3f3'
        },
        series: {
          color: '#3c8dbc',
          lines: {
            lineWidth: 2,
            show: true,
            fill: true,
          },
        },
        yaxis: {
          min: 0,
          max: 100,
          show: true
        },
        xaxis: {
          show: true
        }
      }
    )
    var updateInterval = 500 //Fetch data ever x milliseconds
    var realtime       = 'on' //If == to on then fetch data every x seconds. else stop fetching
    function update() {

      interactive_plot.setData([getRandomData()])

      // Since the axes don't change, we don't need to call plot.setupGrid()
      interactive_plot.draw()
      if (realtime === 'on') {
        setTimeout(update, updateInterval)
      }
    }
    //INITIALIZE REALTIME DATA FETCHING
    if (realtime === 'on') {
      update()
    }
    //REALTIME TOGGLE
    $('#realtime .btn').click(function () {
      if ($(this).data('toggle') === 'on') {
        realtime = 'on'
      }
      else {
        realtime = 'off'
      }
      update()
    })
})


$(function () {


  var areaChartData = {
    labels  : ['10⁷', '10⁸', '10⁹', '10¹⁰', '10¹¹', '10¹²'],
    datasets: [
      {
        label               : 'PCFG',
        backgroundColor     : 'rgba(76, 73, 76, 0.7)',
        borderColor         : 'rgba(76, 73, 76, 0.7)',
        pointRadius          : true,
        pointColor          : '#3b8bba',
        pointStrokeColor    : 'rgba(76, 73, 76, 0.7)',
        pointHighlightFill  : 'rgba(76, 73, 76, 0.7)',
        pointHighlightStroke: 'rgba(76, 73, 76, 0.7)',
        data                : [28, 48, 40, 19, 86, 27]
      },
      {
        label               : 'Omen',
        backgroundColor     : 'rgba(130, 125, 130, 0.7)',
        borderColor         : 'rgba(130, 125, 130, 0.7)',
        pointRadius         : false,
        pointColor          : 'rgba(130, 125, 130, 0.7)',
        pointStrokeColor    : '#c1c7d1',
        pointHighlightFill  : 'rgba(130, 125, 130, 0.7)',
        pointHighlightStroke: 'rgba(130, 125, 130, 0.7)',
        data                : [15, 89, 10, 50, 56, 15]
      },
      {
        label               : 'PassGAN',
        backgroundColor     : 'rgba(0, 209, 29, 0.7)',
        borderColor         : 'rgba(0, 209, 29, 0.7)',
        pointRadius         : false,
        pointColor          : 'rgba(0, 209, 29, 0.7)',
        pointStrokeColor    : '#c1c7d1',
        pointHighlightFill  : 'rgba(0, 209, 29, 0.7)',
        pointHighlightStroke: 'rgba(0, 209, 29, 0.7)',
        data                : [35, 69, 10, 11, 96, 55]
      },
      {
        label               : 'PassGPT',
        backgroundColor     : 'rgba(0, 2, 209, 0.7)',
        borderColor         : 'rgba(0, 2, 209, 0.7)',
        pointRadius         : false,
        pointColor          : 'rgba(0, 2, 209, 0.7)',
        pointStrokeColor    : '#c1c7d1',
        pointHighlightFill  : 'rgba(0, 2, 209, 0.7)',
        pointHighlightStroke: 'rgba(0, 2, 209, 0.7)',
        data                : [95, 69, 50, 81, 8, 12]
      },
      {
        label               : 'PassGPTv2',
        backgroundColor     : 'rgba(209, 0, 193, 0.7)',
        borderColor         : 'rgba(209, 0, 193, 0.7)',
        pointRadius         : false,
        pointColor          : 'rgba(209, 0, 193, 0.7)',
        pointStrokeColor    : '#c1c7d1',
        pointHighlightFill  : '#fff',
        pointHighlightStroke: 'rgba(209, 0, 193, 0.7)',
        data                : [35, 29, 90, 51, 46, 75]
      },
    ]
  }

  var areaChartOptions = {
    maintainAspectRatio : true,
    responsive : true,
    legend: {
      display: true
    },
    scales: {
      xAxes: [{
        gridLines : {
          display : true,
        }
      }],
      yAxes: [{
        gridLines : {
          display : true,
        }
      }]
    }
  }


  //-------------
  //- LINE CHART -
  //--------------
  var lineChartCanvas = $('#lineChart').get(0).getContext('2d')
  var lineChartOptions = jQuery.extend(true, {}, areaChartOptions)
  var lineChartData = jQuery.extend(true, {}, areaChartData)
  lineChartData.datasets[0].fill = false;
  lineChartData.datasets[1].fill = false;
  lineChartData.datasets[2].fill = false;
  lineChartData.datasets[3].fill = false;
  lineChartData.datasets[4].fill = false;
  lineChartOptions.datasetFill = true;

  var lineChart = new Chart(lineChartCanvas, { 
    type: 'line',
    data: lineChartData, 
    options: lineChartOptions
  })

  //-------------
  //- DONUT CHART -
  //-------------
  // Get context with jQuery - using jQuery's .get() method.
  
})