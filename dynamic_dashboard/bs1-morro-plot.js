let opts = {
    id: "chart1",
    class: "my-chart",
    width: 900,
    height: 300,
    series: [
        {},
        {
            // initial toggled state (optional)
            show: true,
            spanGaps: false,
            // series style
            width: 3,
        }
    ],
    axes: [
        {
        //	size: 30,
 
        },
        {
            labelSize: 40
        }
    ],
};

function calc_mean(array) {
    var total = 0;
    var count = 0;
    array.forEach(function(item, index) {
        if (item != "null") {
            total += item;
            count++;
        };
    });

    return (total / count).toFixed(2);
};

function get_latest_value(array) {
    for (let i = array.length - 1; i >= 0; i--) {
        if (array[i] != "null") {
            return [array[i], i];
        };
    };
};

function canvas_arrow(context, fromx, fromy, tox, toy) {
    var headlen = 10; // length of head in pixels
    var dx = tox - fromx;
    var dy = toy - fromy;
    var angle = Math.atan2(dy, dx);
    ctx.lineWidth = 8;

    context.moveTo(fromx, fromy);
    context.lineTo(tox, toy);
    context.lineTo(tox - headlen * Math.cos(angle - Math.PI / 6), toy - headlen * Math.sin(angle - Math.PI / 6));
    context.moveTo(tox, toy);
    context.lineTo(tox - headlen * Math.cos(angle + Math.PI / 6), toy - headlen * Math.sin(angle + Math.PI / 6));
  }

function draw_slope_arrow(context, slope, scale_offset) {
    context.beginPath();
    // Scale from units and unit range to canvas height values (0-100 px)
    // Remember tht canvas y=0 is at the top
    let x  = ((scale_offset/2) - slope) * (100/scale_offset)

    // fromx, fromy, tox, toy
    canvas_arrow(context, 0, 100-x, 120, x);
    context.stroke();
};


  
// var json_file = "/data/oyster-dash-proto/dynamic_dashboard/demo_data.json";
var json_file = "edu_calpoly_marine_morro.json";

fetch(json_file)
    .then(response => {
        return response.json();
    })
    .then(data2 => {
        let parent_div = document.getElementsByClassName('plots')[0];

        
        let plot_vars = ["Temperature", 'Dissolved Oxygen', 'Chlorophyll-a','pH'];
        let plot_colors = ['red', 'blue', 'green','purple']
        let i = 0;

        // let last_date = Date(get_last_timestamp(data2['datetime']) * 1000).toLocaleString(); // multiply by 1000 to convert to milliseconds
        
        do {
            let d = [data2['datetime'], data2[plot_vars[i]]['values']];
            opts['series'][1]['label'] = plot_vars[i];
            opts['series'][1]['stroke'] = plot_colors[i];
            opts['axes'][1]['label'] = `${plot_vars[i]} [${data2[plot_vars[i]]['units']}]`;
            opts['axes'][1]['stroke'] = plot_colors[i];
            let div_id = plot_vars[i].replace(/\s/g, '-').toLowerCase()
            
            // generate a row for each plot and Mean value
            let row_div = document.createElement("div");
            row_div.classList.add("row");
            row_div.style.display = 'flex';
            row_div.style.alignItems = 'center';            
            parent_div.appendChild(row_div);

            
            // Generate a div for each plot
            let plot_div = document.createElement("div", {id: div_id});
            plot_div.classList.add("col-8");
            plot_div.style.display = 'inline';
            plot_div.style.float = 'left';
            row_div.appendChild(plot_div);
            uPlot(opts, d, id=plot_div);
            

            // Calculate Mean for the entire timeseries
            let total_mean = calc_mean(data2[plot_vars[i]]['values']);
            

            let var_mean_elem = document.createElement('p');
            var_mean_elem.innerHTML = `14-day Avg: ${total_mean} ${data2[plot_vars[i]]['units']}`;
            var_mean_elem.style.color = "black";
            var_mean_elem.style.fontWeight = 'bold';
            var_mean_elem.style.fontSize = '20px';
            
            // Latest value
            let var_last_elem = document.createElement('p');
            let last_value = get_latest_value(data2[plot_vars[i]]['values']);
            var_last_elem.innerHTML = `${last_value[0]} ${data2[plot_vars[i]]['units']}`;
            

            let last_date_milli = data2['datetime'][last_value[1]] * 1000; // multiply by 1000 to convert to milliseconds
            let last_date = new Date(last_date_milli).toLocaleString();
            
            var_last_elem.style.color = plot_colors[i];
            var_last_elem.style.fontWeight = 'bold';
            var_last_elem.style.fontSize = '35px';
            var_last_elem.style.marginBottom = '0px';

            let var_last_date = document.createElement('p');
            var_last_date.innerHTML = `${last_date}`;
            var_last_date.style.color = "black";
            var_last_date.style.fontSize = '10px';
            var_last_date.style.marginTop = '0px';

            // Create Canvas for arrow
            let c = document.createElement('canvas');
            c.setAttribute("id", `c-${i}}`); // New id for each variable
            c.setAttribute("width", "150");
            c.setAttribute("height", "100");
            
            // Generate a div for Mean values using BS
            let mean_div = document.createElement("div");
            mean_div.classList.add("col-4");
            // mean_div.appendChild(var_name_elem);
            mean_div.appendChild(var_last_elem);
            mean_div.appendChild(var_last_date);
            mean_div.appendChild(c);
            mean_div.appendChild(var_mean_elem);
            row_div.appendChild(mean_div);
            if (data2[plot_vars[i]].slope != null) {
                ctx = document.getElementById(`c-${i}}`).getContext("2d");
                ctx.strokeStyle = plot_colors[i];
                draw_slope_arrow(ctx, data2[plot_vars[i]].slope , data2[plot_vars[i]].slope_scale);

            };
            i++;
        } while (i < plot_vars.length);
        
        
        // let uplot = new uPlot(opts, d, body.plot1);
    
    });

