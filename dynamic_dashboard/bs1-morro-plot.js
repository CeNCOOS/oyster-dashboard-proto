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
    var latest_value = array[array.length - 1];
    return latest_value;
};


fetch("./demo_data.json")
    .then(response => {
        return response.json();
    })
    .then(data2 => {
        let parent_div = document.getElementsByClassName('plots')[0];

        
        let plot_vars = ["Temperature", 'Dissolved Oxygen', 'Chlorophyll-a'];
        let plot_colors = ['red', 'blue', 'green']
        let i = 0;
        do {
            let d = [data2['datetime'], data2[plot_vars[i]]['values']];
            opts['series'][1]['label'] = plot_vars[i];
            opts['series'][1]['stroke'] = plot_colors[i];
            opts['axes'][1]['label'] = plot_vars[i];
            opts['axes'][1]['stroke'] = plot_colors[i];
            let div_id = plot_vars[i].replace(/\s/g, '-').toLowerCase()
            
            // generate a row for each plot and Mean value
            let row_div = document.createElement("div");
            row_div.classList.add("row");
            // row_div.classList.add("vertical-align");
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
            // let var_name_elem = document.createElement('p');
            // var_name_elem.innerHTML = `${plot_vars[i]}`;
            // var_name_elem.style.color = plot_colors[i];
            // var_name_elem.style.fontWeight = 'bold';
            // var_name_elem.style.fontSize = '20px';

            let var_mean_elem = document.createElement('p');
            var_mean_elem.innerHTML = `14-day Avg: ${total_mean} ${data2[plot_vars[i]]['units']}`;
            var_mean_elem.style.color = "black";
            var_mean_elem.style.fontWeight = 'bold';
            var_mean_elem.style.fontSize = '20px';
            
            // Latest value
            let var_last_elem = document.createElement('p');
            var_last_elem.innerHTML = `${get_latest_value(data2[plot_vars[i]]['values'])} ${data2[plot_vars[i]]['units']}`;
            var_last_elem.style.color = plot_colors[i];
            var_last_elem.style.fontWeight = 'bold';
            var_last_elem.style.fontSize = '35px';
            var_last_elem.style.marginBottom = '0px';

            // Generate a div for Mean values using BS
            let mean_div = document.createElement("div");
            mean_div.classList.add("col-4");
            // mean_div.appendChild(var_name_elem);
            mean_div.appendChild(var_last_elem);
            mean_div.appendChild(var_mean_elem);
            row_div.appendChild(mean_div);

            
            i++;
        } while (i < plot_vars.length);

        // let uplot = new uPlot(opts, d, body.plot1);
    
    });