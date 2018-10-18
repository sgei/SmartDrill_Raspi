// ---------------------------------------------------------------------------
// time & date on console
var log = console.log;

console.log = function() {
	var first_parameter = arguments[0];
	var other_parameters = Array.prototype.slice.call(arguments, 1);

	function formatConsoleDate(date) {
		var hour = date.getHours();
		var minutes = date.getMinutes();
		var seconds = date.getSeconds();
		var milliseconds = date.getMilliseconds();

		return '[' +
			((hour < 10) ? '0' + hour : hour) +
			':' +
			((minutes < 10) ? '0' + minutes : minutes) +
			':' +
			((seconds < 10) ? '0' + seconds : seconds) +
			'] ';
	}

	log.apply(console, [formatConsoleDate(new Date()) + first_parameter].concat(other_parameters));
};

// ---------------------------------------------------------------------------

// VARIABLES

var address_receiver = "0xa29fbde7ff9cbac4bc950eff24ef7a0de532f927";
var address_sender = "0xb7ce3a62ad5a3ec33eaf0d65ae69f5f1714ba2c1";

// ---------------------------------------------------------------------------

// MODULES
// importing config file
var config = require('./config.json');
// module for file operations
var fs = require('fs');
// web3 javscript library
var Web3 = require("web3");
var provider = new Web3.providers.HttpProvider('http://localhost:8545');
var web3 = new Web3(provider);
// http module
var http = require('http');
// event module
var events = require('events');
var eventObject = new events.EventEmitter();
module.exports = eventObject;
// ---------------------------------------------------------------------------

// CODE

console.log("script started, waiting for changes")

// watch drill.dat with watchFile for changes
fs.watchFile(config.path + "drill.dat", function(eventName, filename) {
	// read drill.dat with readFile after changes have been made
	fs.readFile(config.path + "drill.dat", "utf8", function(err, data) {
		// error handling
		if (err) {
			console.log(err);
		} else {

			var usage_raw = data.toString().split("\n");

			var usage_1, usage_2, usage_3;

			usage_raw.forEach(function(value) {
				if (value.startsWith("USAGE_TIME_MODE_1")) {
					usage_1 = parseInt(value.split("=")[1]);
					//console.log(usage_1);
				}
				if (value.startsWith("USAGE_TIME_MODE_2")) {
					usage_2 = parseInt(value.split("=")[1]);
					//console.log(usage_2);
				}
				if (value.startsWith("USAGE_TIME_MODE_3")) {
					usage_3 = parseInt(value.split("=")[1]);
					//console.log(usage_3);
				}
			})

			// add each time per mode together
			// you can use the multiplcators in config.json to chance prices per mode

			var time_usage =
				(
					((usage_1 * config.payment.usage_multiplicator_1) +
						(usage_2 * config.payment.usage_multiplicator_2) +
						(usage_3 * config.payment.usage_multiplicator_3)) * (10**18)
				);

			console.log("eth-pi: time used is " + (time_usage / (10**18)) + " seconds");

			// check the wallet for later comparing
			web3.eth.getBalance(address_receiver, function(error, result) {
				if (error) {
					console.log("eth-pi: wallet could not be found")
				}
				// write wallet value into variable
				var time_paid = result;
				console.log("eth-pi: time paid is " + (time_paid / (10**18)) + " seconds");

				// ---------------------------------------------------------------------------

				///// HTTP STUFF

				// sending POST request to IoT hub

				var options = {
					host: 'deviceservicea.azurewebsites.net',
					port: 80,
					path: '/devices/473095323502/paidUnits',
					method: 'POST'
				};

				var req = http.request(options, function(res) {
					console.log(res.statusCode);
				});
				req.write(time_paid.toString());
				req.end();


				// ---------------------------------------------------------------------------

				///// COMPARE TIME_USED & TIME PAID

				// ------------------------------

				// behaviour the device is used less than paid
				// nothingh as to be done, everything is okay
				if (time_usage < (config.payment.lower_percentage * time_paid)) {
					console.log("eth-pi: time_usage < time_paid");
					console.log("eth-pi: device can stay activated")
				}

				// ------------------------------

				// behaviour the device is close to beeing not paid or slightly not paid
				else if (time_usage < (config.payment.upper_percentage * time_paid) || time_usage == time_paid) {
					console.log("eth-pi: time_usage near to time_paid");
					// try to send ether to wallet
					web3.eth.sendTransaction({
							from: address_sender,
							to: address_receiver,
							value: (config.payment.amount * (10**18))
						},
						function(err, transactionHash) {
							if (!err) {
								// smart device can run
								console.log("eth-pi: transaction with hash " + transactionHash + " has been sent");
								// get belenace for console output
								web3.eth.getBalance(address_receiver, function(error, result) {
									console.log("eth-pi: new time paid is " + (result / (10**18)) + " seconds");
								});
								// delete file on startup
								fs.unlink(config.path + "lock_local", function(err) {
									if (err) {
										"eth-pi: something went wrong while deleting"
									} else {
										console.log("eth-pi: lock file has been deleted");
									}
								})
							} else {
								console.log("eth-pi: out of money")
								console.log("eth-pi: transaction has not been send");
								// create LOCK file when usage is equal or above paid time
								if ((time_usage == time_paid) || (time_usage > time_paid)) {
									fs.writeFile(config.path + "lock_local", "LOCKED", function(err) {
										if (err) throw err;
										console.log("eth-pi: lock file has been created");
										console.log("eth-pi: shutdown device")
									})
								} else {
									// wait for the usage to be equal or above paid time
									console.log("eth-pi: waiting for last usage");
								}
							}
						}
					)
				}

				// -------------------------

				// behaviour when device is not paid but used
				// this could happen on startup when values @ drill.dat are not zero
				else {
					// try to send transaction to pay for usage
					web3.eth.sendTransaction({
							from: address_sender,
							to: address_receiver,
							value: (config.payment.amount * (10**18))
						},
						function(err, transactionHash) {
							if (!err) {
								// smart device can run
								console.log("eth-pi: transaction with hash " + transactionHash + " has been sent");
								// inform about new balance
								web3.eth.getBalance(address_receiver, function(error, result) {
									console.log("eth-pi: time used is " + (time_usage / (10**18)) + " seconds");
								});
								// delete LOCK file
								fs.unlink(config.path + "lock_local", function(err) {
									if (err) {} else {
										console.log("eth-pi: lock file has been deleted");
									}
								})
							} else {
								console.log("eth pi: out of money");
								console.log("eth-pi: shutting down device");
								// create LOCK file
								fs.writeFile(config.path + "lock_local", "LOCKED", function(err) {
									if (err) {
										throw err;
									}
									console.log("eth-pi: lock file has been created");
								})
							}
						}
					)
				}
			})
		}
	})
});