var ctx = document.getElementById('myChartBar');
var yAxesticks = [];
var highestVal;
var myChartBar = new Chart(ctx, {
		type: 'bar',
		data: {
				labels: ['1 año', '2 años', '3 años', '4 años', '5 años', '6 años', '7 años', '8 años', '9 años', '10 años'],
				datasets: [{
						label: 'Inversion anual',
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
						xAxes: [{
								cornerRadius: 20,
								stacked: true,
								barPercentage: 0.4
						}],
						yAxes: [{
								ticks: {
										beginAtZero: true,
										stepSize: 20000,
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
var ctx = document.getElementById('myChartPie');
var myChartPie = new Chart(ctx, {
		type: 'pie',
		data: {
				labels: ["Inversión Inicial", "Utilidad"],
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

var ctx = document.getElementById('myChartBarTest');
window.onload = function() {
	var myChartBarTest = new Chart(ctx, {
			type: 'bar',
			data: {
					labels: ['1 año', '2 años', '3 años', '4 años', '5 años', '6 años', '8 años', '9 años', '10 años'],
					datasets: [{
							label: 'Inversion anual',
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
							xAxes: [{
									cornerRadius: 20,
									stacked: true,
									barPercentage: 0.4
							}],
							yAxes: [{
									ticks: {
											beginAtZero: true,
											stepSize: 20000,
											max: 100000,
											// Return an empty string to draw the tick line but hide the tick label
											// Return `null` or `undefined` to hide the tick line entirely
											userCallback: function(value, index, values) {
												// Convert the number to a string and splite the string every 3 charaters from the end
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
};
function rellenarForm(){
	
}


function updateChart(){
	//obtener valores
	var nyears = 10;
	var nmonths = 12;
	var valor_global = jQuery("#valor_global").val();
	var meses_global = jQuery("#meses_global").val();
	var meses_global = jQuery("#meses_global").val();
	var valor_anual = jQuery("#valor_anual").val();
	var input_value = jQuery("#valor_mensual").val();
	var rentabilidad = jQuery("#rentabilidad").val();
 
	//Quitar simbolo $
	var valor_mensual_neto = Number(input_value.replace(/[^0-9.-]+/g,""));
	var valor_anual_neto = Number(valor_anual.replace(/[^0-9.-]+/g,""));
	var valor_global_neto = Number(valor_global.replace(/[^0-9.-]+/g,""));

	//operaciones
	var total_anual = (valor_mensual_neto * nmonths).toFixed(2);
	var rate = rentabilidad / 100;
	var interest = (total_anual * rate).toFixed(2);
	var balance = parseFloat(total_anual) + parseFloat(interest);
	

	//convertir currency  e imprimir
	jQuery("#valor_mensual").val('$' + parseFloat(valor_mensual_neto, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#valor_anual").val('$' + parseFloat(total_anual, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());

	//calculos anual inflacion
	var inflacionAñoUno = total_anual;
	var inflacionAñoDos = (inflacionAñoUno * 1.03).toFixed(2);
	var inflacionAñoTres = (inflacionAñoDos * 1.03).toFixed(2);
	var inflacionAñoCuatro = (inflacionAñoTres * 1.03).toFixed(2);
	var inflacionAñoCinco = (inflacionAñoCuatro * 1.03).toFixed(2);
	var inflacionAñoSeis = (inflacionAñoCinco * 1.03).toFixed(2);
	var inflacionAñoSiete = (inflacionAñoSeis * 1.03).toFixed(2);
	var inflacionAñoOcho = (inflacionAñoSiete * 1.03).toFixed(2);
	var inflacionAñoNueve = (inflacionAñoOcho * 1.03).toFixed(2);
	var inflacionAñoDiez = (inflacionAñoNueve * 1.03).toFixed(2);

	//calculos año uno inversion
	var añoUnoInit = total_anual ;
	var interesAñoUno = (total_anual * rate).toFixed(2);
	var totalAñoUno = (parseFloat(añoUnoInit) + parseFloat(interesAñoUno)).toFixed(2);

	var sumaPruebaUno = total_anual;


	//calculos año dos inversion
	var añoDosInit = (parseFloat(totalAñoUno) + parseFloat(inflacionAñoDos)).toFixed(2) ;
	var interesAñoDos = (añoDosInit * rate).toFixed(2);
	var totalAñoDos = (parseFloat(añoDosInit) + parseFloat(interesAñoDos)).toFixed(2);

	
	var sumaPruebaDos = (parseFloat(sumaPruebaUno) + parseFloat(inflacionAñoDos)).toFixed(2);

	//calculos año tres inversion
	var añoTresInit = (parseFloat(totalAñoDos) + parseFloat(inflacionAñoTres)).toFixed(2) ;
	var interesAñoTres = (añoTresInit * rate).toFixed(2);
	var totalAñoTres = (parseFloat(añoTresInit) + parseFloat(interesAñoTres)).toFixed(2);

	var sumaPruebaTres = (parseFloat(sumaPruebaDos) + parseFloat(inflacionAñoTres)).toFixed(2);

	//calculos año Cuatro inversion
	var añoCuatroInit = (parseFloat(totalAñoTres) + parseFloat(inflacionAñoCuatro)).toFixed(2) ;
	var interesAñoCuatro = (añoCuatroInit * rate).toFixed(2);
	var totalAñoCuatro = (parseFloat(añoCuatroInit) + parseFloat(interesAñoCuatro)).toFixed(2);

	var sumaPruebaCuatro = (parseFloat(sumaPruebaTres) + parseFloat(inflacionAñoCuatro)).toFixed(2);

	//calculos año Cinco inversion
	var añoCincoInit = (parseFloat(totalAñoCuatro) + parseFloat(inflacionAñoCinco)).toFixed(2) ;
	var interesAñoCinco = (añoCincoInit * rate).toFixed(2);
	var totalAñoCinco = (parseFloat(añoCincoInit) + parseFloat(interesAñoCinco)).toFixed(2);

	var sumaPruebaCinco = (parseFloat(sumaPruebaCuatro) + parseFloat(inflacionAñoCinco)).toFixed(2);

	//calculos año Seis inversion
	var añoSeisInit = (parseFloat(totalAñoCinco) + parseFloat(inflacionAñoSeis)).toFixed(2) ;
	var interesAñoSeis = (añoSeisInit * rate).toFixed(2);
	var totalAñoSeis = (parseFloat(añoSeisInit) + parseFloat(interesAñoSeis)).toFixed(2);

	var sumaPruebaSeis = (parseFloat(sumaPruebaCinco) + parseFloat(inflacionAñoSeis)).toFixed(2);

	//calculos año Siete inversion
	var añoSieteInit = (parseFloat(totalAñoSeis) + parseFloat(inflacionAñoSiete)).toFixed(2) ;
	var interesAñoSiete = (añoSieteInit * rate).toFixed(2);
	var totalAñoSiete= (parseFloat(añoSieteInit) + parseFloat(interesAñoSiete)).toFixed(2);

	var sumaPruebaSiete = (parseFloat(sumaPruebaSeis) + parseFloat(inflacionAñoSiete)).toFixed(2);

	//calculos año Ocho inversion
	var añoOchoInit = (parseFloat(totalAñoSiete) + parseFloat(inflacionAñoOcho)).toFixed(2) ;
	var interesAñoOcho = (añoOchoInit * rate).toFixed(2);
	var totalAñoOcho = (parseFloat(añoOchoInit) + parseFloat(interesAñoOcho)).toFixed(2);

	var sumaPruebaOcho = (parseFloat(sumaPruebaSiete) + parseFloat(inflacionAñoOcho)).toFixed(2);

	//calculos año Nueve inversion
	var añoNueveInit = (parseFloat(totalAñoOcho) + parseFloat(inflacionAñoNueve)).toFixed(2) ;
	var interesAñoNueve = (añoNueveInit * rate).toFixed(2);
	var totalAñoNueve = (parseFloat(añoNueveInit) + parseFloat(interesAñoNueve)).toFixed(2);
	
	var sumaPruebaNueve = (parseFloat(sumaPruebaOcho) + parseFloat(inflacionAñoNueve)).toFixed(2);

	//calculos año Diez inversion
	var añoDiezInit = (parseFloat(totalAñoNueve) + parseFloat(inflacionAñoDiez)).toFixed(2) ;
	var interesAñoDiez = (añoDiezInit * rate).toFixed(2);
	var totalAñoDiez = (parseFloat(añoDiezInit) + parseFloat(interesAñoDiez)).toFixed(2);

	var sumaPruebaDiez = (parseFloat(sumaPruebaNueve) + parseFloat(inflacionAñoDiez)).toFixed(2);


	var sumaInversionTotal = (parseFloat(inflacionAñoUno) + parseFloat(inflacionAñoDos) + parseFloat(inflacionAñoTres) + parseFloat(inflacionAñoCuatro) + parseFloat(inflacionAñoCinco) + parseFloat(inflacionAñoSeis) + parseFloat(inflacionAñoSiete) + parseFloat(inflacionAñoOcho) + parseFloat(inflacionAñoNueve) + parseFloat(inflacionAñoDiez)).toFixed(2);
	var sumaInteresesTotal = (parseFloat(interesAñoUno) + parseFloat(interesAñoDos) + parseFloat(interesAñoTres) + parseFloat(interesAñoCuatro) + parseFloat(interesAñoCinco) + parseFloat(interesAñoSeis) + parseFloat(interesAñoSiete) + parseFloat(interesAñoOcho) + parseFloat(interesAñoNueve) + parseFloat(interesAñoDiez)).toFixed(2);


	myChartBar.data.datasets[0].data  = [inflacionAñoUno, inflacionAñoDos, inflacionAñoTres, inflacionAñoCuatro, inflacionAñoCinco, inflacionAñoSeis, inflacionAñoSiete, inflacionAñoOcho, inflacionAñoNueve, inflacionAñoDiez];
	myChartBar.data.datasets[1].data  = [totalAñoUno, totalAñoDos, totalAñoTres, totalAñoCuatro, totalAñoCinco, totalAñoSeis, totalAñoSiete, totalAñoOcho, totalAñoNueve, totalAñoDiez];
	myChartBar.update();

	// myChartBarTest.data.datasets[0].data  = [sumaPruebaUno, sumaPruebaDos, sumaPruebaTres, sumaPruebaCuatro, sumaPruebaCinco, sumaPruebaSeis, sumaPruebaSiete, sumaPruebaOcho, sumaPruebaNueve, sumaPruebaDiez];
	// myChartBarTest.data.datasets[1].data  = [totalAñoUno, totalAñoDos, totalAñoTres, totalAñoCuatro, totalAñoCinco, totalAñoSeis, totalAñoSiete, totalAñoOcho, totalAñoNueve, totalAñoDiez];
	// myChartBarTest.update();


	myChartPie.data.datasets[0].data  = [sumaInversionTotal, sumaInteresesTotal];
	myChartPie.update();

	jQuery("#valor_global").val('$' + parseFloat(totalAñoDiez, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery(".graficas-op").css('display', 'flex');

	jQuery("#valor_mensual_month").val(input_value);
	jQuery("#valor_global_pop").val('$' + parseFloat(totalAñoDiez, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#valor_mensual_month_pop").val('$' + parseFloat(valor_mensual_neto, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#rentabilidad_pop").val(rentabilidad);

	jQuery("#inflacionUnoMonth").text('$' + parseFloat(inflacionAñoUno, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inflacionDosMonth").text('$' + parseFloat(inflacionAñoDos, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inflacionTresMonth").text('$' + parseFloat(inflacionAñoTres, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inflacionCuatroMonth").text('$' + parseFloat(inflacionAñoCuatro, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inflacionCincoMonth").text('$' + parseFloat(inflacionAñoCinco, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inflacionSeisMonth").text('$' + parseFloat(inflacionAñoSeis, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inflacionSieteMonth").text('$' + parseFloat(inflacionAñoSiete, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inflacionOchoMonth").text('$' + parseFloat(inflacionAñoOcho, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inflacionNueveMonth").text('$' + parseFloat(inflacionAñoNueve, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inflacionDiezMonth").text('$' + parseFloat(inflacionAñoDiez, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());


	jQuery("#inversionUnoMonth").text('$' + parseFloat(añoUnoInit, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inversionDosMonth").text('$' + parseFloat(añoDosInit, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inversionTresMonth").text('$' + parseFloat(añoTresInit, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inversionCuatroMonth").text('$' + parseFloat(añoCuatroInit, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inversionCincoMonth").text('$' + parseFloat(añoCincoInit, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inversionSeisMonth").text('$' + parseFloat(añoSeisInit, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inversionSieteMonth").text('$' + parseFloat(añoSieteInit, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inversionOchoMonth").text('$' + parseFloat(añoOchoInit, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inversionNueveMonth").text('$' + parseFloat(añoNueveInit, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#inversionDiezMonth").text('$' + parseFloat(añoDiezInit, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());

	jQuery("#interesesUnoMonth").text('$' + parseFloat(interesAñoUno, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#interesesDosMonth").text('$' + parseFloat(interesAñoDos, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#interesesTresMonth").text('$' + parseFloat(interesAñoTres, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#interesesCuatroMonth").text('$' + parseFloat(interesAñoCuatro, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#interesesCincoMonth").text('$' + parseFloat(interesAñoCinco, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#interesesSeisMonth").text('$' + parseFloat(interesAñoSeis, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#interesesSieteMonth").text('$' + parseFloat(interesAñoSiete, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#interesesOchoMonth").text('$' + parseFloat(interesAñoOcho, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#interesesNueveMonth").text('$' + parseFloat(interesAñoNueve, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#interesesDiezMonth").text('$' + parseFloat(interesAñoDiez, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());

	jQuery("#saldoUnoMonth").text('$' + parseFloat(totalAñoUno, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#saldoDosMonth").text('$' + parseFloat(totalAñoDos, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#saldoTresMonth").text('$' + parseFloat(totalAñoTres, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#saldoCuatroMonth").text('$' + parseFloat(totalAñoCuatro, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#saldoCincoMonth").text('$' + parseFloat(totalAñoCinco, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#saldoSeisMonth").text('$' + parseFloat(totalAñoSeis, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#saldoSieteMonth").text('$' + parseFloat(totalAñoSiete, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#saldoOchoMonth").text('$' + parseFloat(totalAñoOcho, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#saldoNueveMonth").text('$' + parseFloat(totalAñoNueve, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
	jQuery("#saldoDiezMonth").text('$' + parseFloat(totalAñoDiez, 10).toFixed(2).replace(/(\d)(?=(\d{3})+\.)/g, "$1,").toString());
};

