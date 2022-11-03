var ctx = document.getElementById('myChartBarOne');
var yAxesticks = [];
var highestVal;
var myChartBarOne = new Chart(ctx, {
		type: 'bar',
		data: {
				labels: ['1 año', '2 años', '3 años', '4 años', '5 años', '6 años', '7 años', '8 años', '9 años', '10 años'],
				datasets: [{
						label: 'Inversion unica',
						data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0 ],
						backgroundColor: [
								'rgba(1, 134, 105, 1)',
								'rgba(1, 134, 105, 1)',
								'rgba(1, 134, 105, 1)',
								'rgba(1, 134, 105, 1)',
								'rgba(1, 134, 105, 1)',
								'rgba(1, 134, 105, 1)',
								'rgba(1, 134, 105, 1)',
								'rgba(1, 134, 105, 1)',
								'rgba(1, 134, 105, 1)',
								'rgba(1, 134, 105, 1)'
						]
				}, {
					label: 'Total ingresos',
					data: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
					backgroundColor: [
							'rgba(249, 224, 158, 1)',
							'rgba(249, 224, 158, 1)',
							'rgba(249, 224, 158, 1)',
							'rgba(249, 224, 158, 1)',
							'rgba(249, 224, 158, 1)',
							'rgba(249, 224, 158, 1)',
							'rgba(249, 224, 158, 1)',
							'rgba(249, 224, 158, 1)',
							'rgba(249, 224, 158, 1)',
							'rgba(249, 224, 158, 1)'
					]
			}],

		},
		options: {

				scales: {
						x: [{
								cornerRadius: 20,
								stacked: true,
								barPercentage: 0.4
						}],
						y: [{
								ticks: {
										beginAtZero: true,
										stepSize: 500,
										// Return an empty string to draw the tick line but hide the tick label
										// Return `null` or `undefined` to hide the tick line entirely
										userCallback: function(value, index, values) {
											// Convert the number to a string and splite the string every 3 charaters from the end
											yAxesticks = values;
											value = value.toString();
											value = value.split(/(?=(?:...)*$)/);

											// Convert the array to a string and format the output
											value = value.join('.');
											return '$' + value;
										}		
									}
									
								}]
							},
							tooltips: { 
								callbacks: {
												label: function(tooltipItem, data) {
													return " $ " + tooltipItem.yLabel;
												},
											}
									}
				}
});
highestVal = yAxesticks[0];
var ctx2 = document.getElementById('myChartPieOne');
var myChartPieOne = new Chart(ctx2, {
		type: 'pie',
		data: {
				labels: ["Inversión Inicial", "Intereses ganados"],
				datasets: [{
						label: "Ganancias totales)",
						backgroundColor: ["#018669", "#F9E09E"],
						data: [0, 0]
				}]
		},
		options: {
				title: {
						display: false
				},
				legend: {
						position: 'bottom',
				}
		}
});


function rellenarForm(){
	
}


function updateChartOne(){
	//obtener valores
	var valor_anual = jQuery("#valor_mensual_one").val();
	var rentabilidad = jQuery("#rentabilidad_one").val();

	//Quitar simbolo 
	var valor_anual_neto = Number(valor_anual.replace(/[^0-9.-]+/g,""));
	var rate = rentabilidad / 100;

	//variables
	var inflacionAñoUnoOne = valor_anual_neto;
	var priceInitUno =  valor_anual_neto * rate;
	var valorfinalUno = (parseFloat(inflacionAñoUnoOne)+parseFloat(priceInitUno)).toFixed(2);

	var inflacionAñoDosOne = valorfinalUno;
	var priceInitDos =  inflacionAñoDosOne * rate;
	var valorfinalDos = (parseFloat(inflacionAñoDosOne)+parseFloat(priceInitDos)).toFixed(2);

	var inflacionAñoTresOne = valorfinalDos;
	var priceInitTres =  inflacionAñoTresOne * rate;
	var valorfinalTres = (parseFloat(inflacionAñoTresOne)+parseFloat(priceInitTres)).toFixed(2);

	var inflacionAñoCuatroOne = valorfinalTres;
	var priceInitCuatro =  inflacionAñoCuatroOne * rate;
	var valorfinalCuatro = (parseFloat(inflacionAñoCuatroOne)+parseFloat(priceInitCuatro)).toFixed(2);

	var inflacionAñoCincoOne = valorfinalCuatro;
	var priceInitCinco =  inflacionAñoCincoOne * rate;
	var valorfinalCinco = (parseFloat(inflacionAñoCincoOne)+parseFloat(priceInitCinco)).toFixed(2);

	var inflacionAñoSeisOne = valorfinalCinco;
	var priceInitSeis =  inflacionAñoSeisOne * rate;
	var valorfinalSeis = (parseFloat(inflacionAñoSeisOne)+parseFloat(priceInitSeis)).toFixed(2);

	var inflacionAñoSieteOne = valorfinalSeis;
	var priceInitSiete =  inflacionAñoSieteOne * rate;
	var valorfinalSiete = (parseFloat(inflacionAñoSieteOne)+parseFloat(priceInitSiete)).toFixed(2);

	var inflacionAñoOchoOne = valorfinalSiete;
	var priceInitOcho =  inflacionAñoOchoOne * rate;
	var valorfinalOcho = (parseFloat(inflacionAñoOchoOne)+parseFloat(priceInitOcho)).toFixed(2);

	var inflacionAñoOchoOne = valorfinalSiete;
	var priceInitOcho =  inflacionAñoOchoOne * rate;
	var valorfinalOcho = (parseFloat(inflacionAñoOchoOne)+parseFloat(priceInitOcho)).toFixed(2);

	var inflacionAñoNueveOne = valorfinalOcho;
	var priceInitNueve =  inflacionAñoNueveOne * rate;
	var valorfinalNueve = (parseFloat(inflacionAñoNueveOne)+parseFloat(priceInitNueve)).toFixed(2);

	var inflacionAñoDiezOne = valorfinalNueve;
	var priceInitDiez =  inflacionAñoDiezOne * rate;
	var valorfinalDiez = (parseFloat(inflacionAñoDiezOne)+parseFloat(priceInitDiez)).toFixed(2);

	

	

	var total_ganancia_one = (valorfinalDiez) - (inflacionAñoUnoOne) ;


	myChartBarOne.data.datasets[0].data  = [inflacionAñoUnoOne, inflacionAñoUnoOne, inflacionAñoUnoOne, inflacionAñoUnoOne, inflacionAñoUnoOne, inflacionAñoUnoOne, inflacionAñoUnoOne, inflacionAñoUnoOne, inflacionAñoUnoOne, inflacionAñoUnoOne];
	myChartBarOne.data.datasets[1].data = [valorfinalUno, valorfinalDos, valorfinalTres, valorfinalCuatro, valorfinalCinco, valorfinalSeis, valorfinalSiete, valorfinalOcho, valorfinalNueve, valorfinalDiez];
	myChartBarOne.update();

	myChartPieOne.data.datasets[0].data  = [inflacionAñoUnoOne, total_ganancia_one];
	myChartPieOne.update();


	jQuery(".graficas-op").css('display', 'flex');
	jQuery("#valor_mensual_one").val(valor_anual);

	jQuery("#inversionUnoOne").text('$' + parseFloat(inflacionAñoUnoOne, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inversionDosOne").text('$' + parseFloat(inflacionAñoDosOne, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inversionTresOne").text('$' + parseFloat(inflacionAñoTresOne, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inversionCuatroOne").text('$' + parseFloat(inflacionAñoCuatroOne, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inversionCincoOne").text('$' + parseFloat(inflacionAñoCincoOne, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inversionSeisOne").text('$' + parseFloat(inflacionAñoSeisOne, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inversionSieteOne").text('$' + parseFloat(inflacionAñoSieteOne, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inversionOchoOne").text('$' + parseFloat(inflacionAñoOchoOne, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inversionNueveOne").text('$' + parseFloat(inflacionAñoNueveOne, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inversionDiezOne").text('$' + parseFloat(inflacionAñoDiezOne, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	
	jQuery("#interesesUnoOne").text('$' + parseFloat(priceInitUno, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#interesesDosOne").text('$' + parseFloat(priceInitDos, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#interesesTresOne").text('$' + parseFloat(priceInitTres, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#interesesCuatroOne").text('$' + parseFloat(priceInitCuatro, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#interesesCincoOne").text('$' + parseFloat(priceInitCinco, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#interesesSeisOne").text('$' + parseFloat(priceInitSeis, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#interesesSieteOne").text('$' + parseFloat(priceInitSiete, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#interesesOchoOne").text('$' + parseFloat(priceInitOcho, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#interesesNueveOne").text('$' + parseFloat(priceInitNueve, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#interesesDiezOne").text('$' + parseFloat(priceInitDiez, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	
	jQuery("#saldoUnoOne").text('$' + parseFloat(valorfinalUno, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#saldoDosOne").text('$' + parseFloat(valorfinalDos, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#saldoTresOne").text('$' + parseFloat(valorfinalTres, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#saldoCuatroOne").text('$' + parseFloat(valorfinalCuatro, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#saldoCincoOne").text('$' + parseFloat(valorfinalCinco, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#saldoSeisOne").text('$' + parseFloat(valorfinalSeis, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#saldoSieteOne").text('$' + parseFloat(valorfinalSiete, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#saldoOchoOne").text('$' + parseFloat(valorfinalOcho, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#saldoNueveOne").text('$' + parseFloat(valorfinalNueve, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#saldoDiezOne").text('$' + parseFloat(valorfinalDiez, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());

	jQuery("#valor_global_one").val('$' + parseFloat((valorfinalDiez), 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());

	jQuery("#valor_global_one_pop").val('$' + parseFloat((valorfinalDiez), 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#valor_mensual_one_pop").val('$' + parseFloat(valor_anual_neto, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#rentabilidad_one_pop").val(rentabilidad);

};

