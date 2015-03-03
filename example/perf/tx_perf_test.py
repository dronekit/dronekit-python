#
# This is the entry point for MavProxy running DroneAPI on the vehicle
# Usage:
# * mavproxy.py
# * module load api
# * api start TestPerformance.py
#

"""
non native test:
mavproxy.py --master=/dev/ttyUSB0,921600 --rtscts --cmd "api start tx_perf_test.py" --max-packets=5000 --daemon

name                                  ncall  tsub      ttot      tavg
..hon2.7/threading.py:752 Thread.run  1      0.000012  3.122469  3.122469
..MAVProxy/mavproxy.py:686 main_loop  1      0.060946  3.122457  3.122457
..mavproxy.py:510 process_master_all  1633   0.013251  2.671116  0.001636
..oxy/mavproxy.py:470 process_master  3406   0.089617  2.657865  0.000780
..tmega.py:6495 MAVLink.parse_buffer  2289   0.022196  2.171655  0.000949
..lotmega.py:6433 MAVLink.parse_char  7399   0.103295  2.164799  0.000293
..otmega.py:6428 MAVLink.__callbacks  5004   0.020360  1.178805  0.000236
...py:230 LinkModule.master_callback  5004   0.261917  1.158446  0.000232
..y:6461 MAVLink.__parse_char_legacy  7399   0.097154  0.835198  0.000113
..b/python2.7/Queue.py:150 Queue.get  871..  0.100600  0.734111  0.000084
..dupilotmega.py:6508 MAVLink.decode  4938   0.267052  0.704184  0.000143
../api.py:243 MPVehicle.send_mavlink  1938   0.015008  0.594257  0.000307
..ardupilotmega.py:6402 MAVLink.send  1958   0.027275  0.528169  0.000270
..erator/mavcrc.py:6 x25crc.__init__  8854   0.048278  0.501256  0.000057
.. MAVLink_command_long_message.pack  3876   0.035650  0.484348  0.000125
..ink.py:407 LinkModule.__to_modules  5004   0.150852  0.436901  0.000087
..143 MAVLink_heartbeat_message.pack  3916   0.080226  0.435734  0.000111
..7/threading.py:309 _Condition.wait  189..  0.043024  0.423701  0.000224
..tor/mavcrc.py:14 x25crc.accumulate  12770  0.381646  0.381646  0.000030
..b/python2.7/Queue.py:107 Queue.put  9184   0.094449  0.336993  0.000037
..y:9626 MAVLink.command_long_encode  1938   0.015715  0.330282  0.000170
..mavcrc.py:23 x25crc.accumulate_str  7832   0.106192  0.291197  0.000037
..link/mavutil.py:726 mavserial.recv  3655   0.016554  0.281399  0.000077
..ial/serialposix.py:453 Serial.read  3655   0.072221  0.264846  0.000072
..mp_module.py:83 ParamModule.master  10611  0.027430  0.246833  0.000023
..oxy/mavproxy.py:651 periodic_tasks  1633   0.077704  0.246205  0.000151
..threading.py:373 _Condition.notify  17897  0.104504  0.244802  0.000014
..oxy/mavproxy.py:188 MPState.master  10611  0.164999  0.219403  0.000021
../python2.7/Queue.py:93 Queue.empty  12462  0.067670  0.215484  0.000017
..77 LinkModule.master_send_callback  1958   0.052664  0.157868  0.000081
...py:228 ParamModule.mavlink_packet  5004   0.022396  0.140830  0.000028
..ink/mavutil.py:736 mavserial.write  1958   0.007324  0.127015  0.000065
..util.py:212 mavserial.post_message  10008  0.100039  0.123820  0.000012
..al/serialposix.py:488 Serial.write  1958   0.030760  0.119692  0.000061
..eading.py:300 _Condition._is_owned  19792  0.056270  0.119383  0.000006
..i.py:247 MPVehicle.message_factory  1938   0.008873  0.074651  0.000039
..ings.py:104 MPSettings.__getattr__  51190  0.070214  0.070214  0.000001
..pi.py:396 APIModule.mavlink_packet  5004   0.035746  0.062572  0.000013

mavproxy.py --master=/dev/ttyUSB0,921600 --rtscts --cmd "api start tx_perf_test.py" --max-packets=5000 --daemon --native
name                                  ncall  tsub      ttot      tavg
..hon2.7/threading.py:752 Thread.run  1      0.000029  2.452683  2.452683
..MAVProxy/mavproxy.py:686 main_loop  1      0.067917  2.452654  2.452654
..mavproxy.py:510 process_master_all  1913   0.014797  1.963876  0.001027
..oxy/mavproxy.py:470 process_master  3829   0.093805  1.949079  0.000509
..tmega.py:6495 MAVLink.parse_buffer  2406   0.021892  1.463879  0.000608
..lotmega.py:6433 MAVLink.parse_char  7437   0.104221  1.440324  0.000194
..otmega.py:6428 MAVLink.__callbacks  5020   0.018822  1.160177  0.000231
...py:230 LinkModule.master_callback  5020   0.263063  1.141356  0.000227
..b/python2.7/Queue.py:150 Queue.get  892..  0.103531  0.653408  0.000073
../api.py:243 MPVehicle.send_mavlink  1958   0.016154  0.604459  0.000309
..ardupilotmega.py:6402 MAVLink.send  1978   0.027734  0.535485  0.000271
.. MAVLink_command_long_message.pack  3916   0.036748  0.495637  0.000127
..143 MAVLink_heartbeat_message.pack  3956   0.083566  0.446711  0.000113
..ink.py:407 LinkModule.__to_modules  5020   0.149475  0.428373  0.000085
..7/threading.py:309 _Condition.wait  195..  0.042275  0.353284  0.000181
..y:9626 MAVLink.command_long_encode  1958   0.015960  0.335833  0.000172
..b/python2.7/Queue.py:107 Queue.put  9404   0.094564  0.332117  0.000035
..mavcrc.py:23 x25crc.accumulate_str  7912   0.107540  0.297585  0.000038
..oxy/mavproxy.py:651 periodic_tasks  1913   0.089161  0.282385  0.000148
..link/mavutil.py:726 mavserial.recv  3848   0.017526  0.269924  0.000070
..erator/mavcrc.py:6 x25crc.__init__  3956   0.021304  0.263655  0.000067
..ial/serialposix.py:453 Serial.read  3848   0.073747  0.252398  0.000066
..mp_module.py:83 ParamModule.master  10964  0.027469  0.252241  0.000023
..threading.py:373 _Condition.notify  18331  0.105160  0.246178  0.000013
..oxy/mavproxy.py:188 MPState.master  10964  0.168562  0.224772  0.000021
../python2.7/Queue.py:93 Queue.empty  12996  0.071587  0.200717  0.000015
..tor/mavcrc.py:14 x25crc.accumulate  7912   0.177303  0.177303  0.000022
..77 LinkModule.master_send_callback  1978   0.053488  0.159170  0.000080
...py:228 ParamModule.mavlink_packet  5020   0.021206  0.137314  0.000027
..y:6423 MAVLink.__parse_char_native  7437   0.017084  0.129977  0.000017
..ink/mavutil.py:736 mavserial.write  1978   0.007265  0.124608  0.000063
..util.py:212 mavserial.post_message  10040  0.100500  0.124568  0.000012
..eading.py:300 _Condition._is_owned  20285  0.057222  0.120491  0.000006
..al/serialposix.py:488 Serial.write  1978   0.032346  0.117342  0.000059
..i.py:247 MPVehicle.message_factory  1958   0.008865  0.075378  0.000038
..ings.py:104 MPSettings.__getattr__  54128  0.075145  0.075145  0.000001
..param.py:232 ParamModule.idle_task  1913   0.015143  0.065751  0.000034
..ython2.7/Queue.py:200 Queue._qsize  23873  0.044139  0.061933  0.000003
..pi.py:396 APIModule.mavlink_packet  5020   0.035728  0.061797  0.000012
..MAVLink_heartbeat_message.__init__  6998   0.043136  0.060533  0.000009

mavproxy.py --master=/dev/ttyUSB0,921600 --rtscts --cmd "api start tx_perf_test.py" --max-packets=5000 --daemon --native --nolog
name                                  ncall  tsub      ttot      tavg
..hon2.7/threading.py:752 Thread.run  1      0.000020  1.909725  1.909725
..MAVProxy/mavproxy.py:686 main_loop  1      0.078463  1.909705  1.909705
..mavproxy.py:510 process_master_all  2355   0.015327  1.343029  0.000570
..oxy/mavproxy.py:470 process_master  4444   0.080486  1.327703  0.000299
..tmega.py:6495 MAVLink.parse_buffer  2618   0.020202  1.026420  0.000392
..lotmega.py:6433 MAVLink.parse_char  7708   0.095572  1.013109  0.000131
..otmega.py:6428 MAVLink.__callbacks  5007   0.017085  0.743219  0.000148
...py:230 LinkModule.master_callback  5007   0.151202  0.726134  0.000145
.. MAVLink_command_long_message.pack  3952   0.036492  0.505875  0.000128 * 0.5, 25% of remaining - can shrink
../api.py:243 MPVehicle.send_mavlink  1976   0.015951  0.455050  0.000230
..143 MAVLink_heartbeat_message.pack  3992   0.084775  0.454919  0.000114
..ink.py:407 LinkModule.__to_modules  5007   0.127681  0.381962  0.000076
..ardupilotmega.py:6402 MAVLink.send  1996   0.028108  0.380732  0.000191
..y:9626 MAVLink.command_long_encode  1976   0.016601  0.346609  0.000175
..oxy/mavproxy.py:651 periodic_tasks  2355   0.094366  0.305242  0.000130
..mavcrc.py:23 x25crc.accumulate_str  7984   0.111864  0.301511  0.000038
..erator/mavcrc.py:6 x25crc.__init__  3992   0.022327  0.265754  0.000067
..mp_module.py:83 ParamModule.master  11413  0.027317  0.253586  0.000022
..oxy/mavproxy.py:188 MPState.master  11413  0.172153  0.226270  0.000020
..link/mavutil.py:726 mavserial.recv  4604   0.020573  0.197259  0.000043
..ial/serialposix.py:453 Serial.read  4604   0.083076  0.176686  0.000038
..tor/mavcrc.py:14 x25crc.accumulate  7984   0.176148  0.176148  0.000022
..y:6423 MAVLink.__parse_char_native  7708   0.017185  0.128009  0.000017
...py:228 ParamModule.mavlink_packet  5007   0.019605  0.123487  0.000025
..ink/mavutil.py:736 mavserial.write  1996   0.007271  0.115052  0.000058
..util.py:212 mavserial.post_message  10014  0.087308  0.108892  0.000011
..al/serialposix.py:488 Serial.write  1996   0.032340  0.107780  0.000054
..i.py:247 MPVehicle.message_factory  1976   0.009835  0.084162  0.000043
..param.py:232 ParamModule.idle_task  2355   0.017717  0.074372  0.000032
..ings.py:104 MPSettings.__getattr__  56145  0.067339  0.067339  0.000001
..MAVLink_heartbeat_message.__init__  7003   0.042130  0.060125  0.000009
..pi.py:396 APIModule.mavlink_packet  5007   0.031268  0.055463  0.000011
..Link_command_long_message.__init__  1976   0.024271  0.047687  0.000024
..til.py:1058 periodic_event.trigger  11776  0.030910  0.038640  0.000003
..y/mavproxy.py:613 set_stream_rates  2356   0.022065  0.032767  0.000014
..k.py:291 LinkModule.__update_state  5007   0.020987  0.029680  0.000006
..proxy_wp.py:105 WPModule.idle_task  2355   0.011025  0.029247  0.000012
../python2.7/Queue.py:93 Queue.empty  2355   0.015377  0.026646  0.000011
..mega.py:43 MAVLink_header.__init__  10995  0.025427  0.025427  0.000002
..MAVLink_heartbeat_message.get_type  37436  0.023302  0.023302  0.000001
..b/mp_module.py:51 APIModule.status  30058  0.020056  0.020056  0.000001
..ilotmega.py:50 MAVLink_header.pack  3992   0.011181  0.019509  0.000005

Same options above, but fixed to remove unneeded pack call (about a 10% speedup on send:
name                                                ncall  tsub      ttot      tavg
/usr/lib/python2.7/threading.py:752 Thread.run      1      0.000012  2.105375  2.105375
..rone/MAVProxy/MAVProxy/mavproxy.py:687 main_loop  1      0.083402  2.105364  2.105364
..roxy/MAVProxy/mavproxy.py:510 process_master_all  2271   0.016510  1.507761  0.000664
..MAVProxy/MAVProxy/mavproxy.py:470 process_master  4357   0.088733  1.491251  0.000342
..s/v10/ardupilotmega.py:6495 MAVLink.parse_buffer  2613   0.022761  1.165566  0.000446
..cts/v10/ardupilotmega.py:6433 MAVLink.parse_char  7720   0.108637  1.147566  0.000149
..ts/v10/ardupilotmega.py:6428 MAVLink.__callbacks  5001   0.019474  0.842866  0.000169
../mavproxy_link.py:230 LinkModule.master_callback  5001   0.173330  0.823391  0.000165
..roneapi/module/api.py:243 MPVehicle.send_mavlink  1982   0.017148  0.554968  0.000280
../dialects/v10/ardupilotmega.py:6402 MAVLink.send  2002   0.031468  0.478323  0.000239
..les/mavproxy_link.py:407 LinkModule.__to_modules  5001   0.145099  0.432095  0.000086
..MAVProxy/MAVProxy/mavproxy.py:651 periodic_tasks  2271   0.106075  0.333850  0.000147
..otmega.py:4418 MAVLink_command_long_message.pack  1982   0.022973  0.308794  0.000156
..upilotmega.py:143 MAVLink_heartbeat_message.pack  2002   0.051051  0.274553  0.000137
..y/modules/lib/mp_module.py:83 ParamModule.master  11334  0.029509  0.272114  0.000024
..MAVProxy/MAVProxy/mavproxy.py:188 MPState.master  11334  0.185972  0.242605  0.000021
..6_64-2.7/pymavlink/mavutil.py:726 mavserial.recv  4566   0.022184  0.209205  0.000046
..t-packages/serial/serialposix.py:453 Serial.read  4566   0.087580  0.187021  0.000041
..ink/generator/mavcrc.py:23 x25crc.accumulate_str  4004   0.072369  0.183322  0.000046
../pymavlink/generator/mavcrc.py:6 x25crc.__init__  2002   0.014129  0.164718  0.000082
..rdupilotmega.py:6423 MAVLink.__parse_char_native  7720   0.019109  0.144126  0.000019
..mavproxy_param.py:228 ParamModule.mavlink_packet  5001   0.022000  0.140084  0.000028
../pymavlink/mavutil.py:212 mavserial.post_message  10002  0.097754  0.122129  0.000012
.._64-2.7/pymavlink/mavutil.py:736 mavserial.write  2002   0.008113  0.122124  0.000061
..-packages/serial/serialposix.py:488 Serial.write  2002   0.033661  0.114011  0.000057
..mavlink/generator/mavcrc.py:14 x25crc.accumulate  4004   0.102416  0.102416  0.000026
..eapi/module/api.py:247 MPVehicle.message_factory  1982   0.009796  0.089112  0.000045
..ules/mavproxy_param.py:232 ParamModule.idle_task  2271   0.019467  0.080866  0.000036
..es/lib/mp_settings.py:104 MPSettings.__getattr__  55391  0.070717  0.070717  0.000001
..lotmega.py:56 MAVLink_heartbeat_message.__init__  7003   0.047517  0.068058  0.000010
..rdupilotmega.py:9452 MAVLink.command_long_encode  1982   0.013160  0.066973  0.000034
..neapi/module/api.py:396 APIModule.mavlink_packet  5001   0.034765  0.061318  0.000012
..ga.py:4403 MAVLink_command_long_message.__init__  1982   0.027512  0.053814  0.000027
..pymavlink/mavutil.py:1058 periodic_event.trigger  11356  0.033456  0.041815  0.000004
..VProxy/MAVProxy/mavproxy.py:613 set_stream_rates  2272   0.024629  0.035985  0.000016
..s/mavproxy_link.py:291 LinkModule.__update_state  5001   0.023399  0.032898  0.000007
..xy/modules/mavproxy_wp.py:105 WPModule.idle_task  2271   0.012621  0.032238  0.000014

New baseline with previous optimiz applied but a longer run

mavproxy.py --master=/dev/ttyUSB0,921600 --rtscts --cmd "api start tx_perf_test.py" --max-packets=20000 --daemon --native --nolog
name                                                ncall  tsub      ttot      tavg
/usr/lib/python2.7/threading.py:752 Thread.run      1      0.000014  9.295308  9.295308
..rone/MAVProxy/MAVProxy/mavproxy.py:687 main_loop  1      0.357102  9.295294  9.295294
..roxy/MAVProxy/mavproxy.py:510 process_master_all  9222   0.073024  6.726796  0.000729
..MAVProxy/MAVProxy/mavproxy.py:470 process_master  17691  0.396538  6.653772  0.000376
..s/v10/ardupilotmega.py:6495 MAVLink.parse_buffer  10787  0.103953  5.217913  0.000484
..cts/v10/ardupilotmega.py:6433 MAVLink.parse_char  30840  0.475240  5.102247  0.000165
..ts/v10/ardupilotmega.py:6428 MAVLink.__callbacks  20001  0.083017  3.773949  0.000189
../mavproxy_link.py:230 LinkModule.master_callback  20001  0.771989  3.690932  0.000185
..roneapi/module/api.py:243 MPVehicle.send_mavlink  7284   0.060705  2.045226  0.000281
..les/mavproxy_link.py:407 LinkModule.__to_modules  20001  0.664688  1.929889  0.000096
../dialects/v10/ardupilotmega.py:6402 MAVLink.send  7362   0.113751  1.770477  0.000240
..MAVProxy/MAVProxy/mavproxy.py:651 periodic_tasks  9222   0.478214  1.513542  0.000164
..otmega.py:4418 MAVLink_command_long_message.pack  7284   0.083047  1.141213  0.000157
..y/modules/lib/mp_module.py:83 ParamModule.master  44230  0.127558  1.115275  0.000025
..upilotmega.py:143 MAVLink_heartbeat_message.pack  7362   0.191518  1.018261  0.000138
..MAVProxy/MAVProxy/mavproxy.py:188 MPState.master  44230  0.751921  0.987717  0.000022
..6_64-2.7/pymavlink/mavutil.py:726 mavserial.recv  17790  0.096199  0.908664  0.000051
..t-packages/serial/serialposix.py:453 Serial.read  17790  0.376893  0.812465  0.000046
..ink/generator/mavcrc.py:23 x25crc.accumulate_str  14724  0.265819  0.676481  0.000046
..rdupilotmega.py:6423 MAVLink.__parse_char_native  30840  0.084953  0.631528  0.000020
..mavproxy_param.py:228 ParamModule.mavlink_packet  20001  0.099333  0.612545  0.000031
../pymavlink/generator/mavcrc.py:6 x25crc.__init__  7362   0.050913  0.606722  0.000082
../pymavlink/mavutil.py:212 mavserial.post_message  40002  0.441143  0.552693  0.000014
.._64-2.7/pymavlink/mavutil.py:736 mavserial.write  7362   0.029389  0.457603  0.000062
..-packages/serial/serialposix.py:488 Serial.write  7362   0.124079  0.428214  0.000058
..mavlink/generator/mavcrc.py:14 x25crc.accumulate  14724  0.379388  0.379388  0.000026
..ules/mavproxy_param.py:232 ParamModule.idle_task  9222   0.088616  0.367637  0.000040
..eapi/module/api.py:247 MPVehicle.message_factory  7284   0.038850  0.325071  0.000045
..es/lib/mp_settings.py:104 MPSettings.__getattr__  220..  0.310079  0.310079  0.000001
..lotmega.py:56 MAVLink_heartbeat_message.__init__  27363  0.194285  0.275280  0.000010
..neapi/module/api.py:396 APIModule.mavlink_packet  20001  0.153114  0.271093  0.000014
..rdupilotmega.py:9452 MAVLink.command_long_encode  7284   0.046631  0.234445  0.000032
..pymavlink/mavutil.py:1058 periodic_event.trigger  46111  0.154911  0.192188  0.000004
..ga.py:4403 MAVLink_command_long_message.__init__  7284   0.096461  0.187814  0.000026
..s/mavproxy_link.py:291 LinkModule.__update_state  20001  0.115403  0.162070  0.000008
..VProxy/MAVProxy/mavproxy.py:613 set_stream_rates  9223   0.106982  0.158716  0.000017
..xy/modules/mavproxy_wp.py:105 WPModule.idle_task  9222   0.058149  0.147688  0.000016
/usr/lib/python2.7/Queue.py:93 Queue.empty          9222   0.074266  0.128052  0.000014
..lotmega.py:81 MAVLink_heartbeat_message.get_type  149..  0.116623  0.116623  0.000001
..oxy/modules/lib/mp_module.py:51 APIModule.status  122..  0.103564  0.103564  0.000001
..es/lib/mp_module.py:36 LinkModule.mavlink_packet  160..  0.097872  0.097872  0.000001
../v10/ardupilotmega.py:43 MAVLink_header.__init__  34725  0.094988  0.094988  0.000003
..xy/modules/lib/mp_module.py:43 LinkModule.module  27666  0.062593  0.093906  0.000003

Same args as previous, but optimzations to iterate only over the modules that have packet/idle
handlers.  (a 30% speedup of master_callback and 10% speedup overall in tx_perf_test)

name                                                ncall  tsub      ttot      tavg
/usr/lib/python2.7/threading.py:752 Thread.run      1      0.000014  7.506126  7.506126
..rone/MAVProxy/MAVProxy/mavproxy.py:695 main_loop  1      0.341018  7.506112  7.506112
..roxy/MAVProxy/mavproxy.py:520 process_master_all  10080  0.064470  5.301439  0.000526
..MAVProxy/MAVProxy/mavproxy.py:480 process_master  18691  0.343054  5.236969  0.000280
..s/v10/ardupilotmega.py:6495 MAVLink.parse_buffer  10922  0.085098  3.990414  0.000365
..cts/v10/ardupilotmega.py:6433 MAVLink.parse_char  31061  0.402903  3.901436  0.000126
..ts/v10/ardupilotmega.py:6428 MAVLink.__callbacks  20002  0.071189  2.773164  0.000139
../mavproxy_link.py:230 LinkModule.master_callback  20002  0.649377  2.701975  0.000135
..roneapi/module/api.py:243 MPVehicle.send_mavlink  7328   0.053543  1.706073  0.000233
../dialects/v10/ardupilotmega.py:6402 MAVLink.send  7406   0.098886  1.474602  0.000199
..les/mavproxy_link.py:408 LinkModule.__to_modules  20002  0.365783  1.235950  0.000062
..MAVProxy/MAVProxy/mavproxy.py:661 periodic_tasks  10080  0.346112  1.176351  0.000117
..otmega.py:4418 MAVLink_command_long_message.pack  7328   0.070202  0.952317  0.000130
..y/modules/lib/mp_module.py:83 ParamModule.master  45160  0.102112  0.937280  0.000021
..upilotmega.py:143 MAVLink_heartbeat_message.pack  7406   0.159165  0.847291  0.000114
..MAVProxy/MAVProxy/mavproxy.py:190 MPState.master  45160  0.639222  0.835168  0.000018
..6_64-2.7/pymavlink/mavutil.py:726 mavserial.recv  18966  0.086703  0.793945  0.000042
..t-packages/serial/serialposix.py:453 Serial.read  18966  0.339244  0.707242  0.000037
..ink/generator/mavcrc.py:23 x25crc.accumulate_str  14812  0.222656  0.562755  0.000038
..rdupilotmega.py:6423 MAVLink.__parse_char_native  31061  0.070296  0.532188  0.000017
../pymavlink/generator/mavcrc.py:6 x25crc.__init__  7406   0.043614  0.509105  0.000069
..mavproxy_param.py:228 ParamModule.mavlink_packet  20002  0.079863  0.493304  0.000025
../pymavlink/mavutil.py:212 mavserial.post_message  40004  0.362677  0.449900  0.000011
.._64-2.7/pymavlink/mavutil.py:736 mavserial.write  7406   0.025578  0.374007  0.000051
..-packages/serial/serialposix.py:488 Serial.write  7406   0.108336  0.348429  0.000047
..ules/mavproxy_param.py:232 ParamModule.idle_task  10080  0.076702  0.320194  0.000032
..mavlink/generator/mavcrc.py:14 x25crc.accumulate  14812  0.313900  0.313900  0.000021
..eapi/module/api.py:247 MPVehicle.message_factory  7328   0.033713  0.288784  0.000039
..es/lib/mp_settings.py:104 MPSettings.__getattr__  228..  0.260477  0.260477  0.000001
..lotmega.py:56 MAVLink_heartbeat_message.__init__  27408  0.162975  0.230682  0.000008
..neapi/module/api.py:396 APIModule.mavlink_packet  20002  0.129320  0.229457  0.000011
..rdupilotmega.py:9452 MAVLink.command_long_encode  7328   0.040013  0.202411  0.000028
..pymavlink/mavutil.py:1058 periodic_event.trigger  50401  0.136115  0.169156  0.000003
..ga.py:4403 MAVLink_command_long_message.__init__  7328   0.083786  0.162398  0.000022
..VProxy/MAVProxy/mavproxy.py:623 set_stream_rates  10081  0.098845  0.144738  0.000014
..s/mavproxy_link.py:292 LinkModule.__update_state  20002  0.099563  0.138054  0.000007
..xy/modules/mavproxy_wp.py:105 WPModule.idle_task  10080  0.051101  0.130417  0.000013
/usr/lib/python2.7/Queue.py:93 Queue.empty          10080  0.066707  0.116093  0.000012
..lotmega.py:81 MAVLink_heartbeat_message.get_type  149..  0.095856  0.095856  0.000001
..xy/modules/lib/mp_module.py:43 LinkModule.module  30240  0.054315  0.083003  0.000003

"""

from pymavlink import mavutil
import time

UPDATE_RATE = 50.0

class PerfTest():
    def __init__(self):
        # First get an instance of the API endpoint
        api = local_connect()

        # get our vehicle - when running with mavproxy it only knows about one vehicle (for now)
        self.vehicle = api.get_vehicles()[0]

        self.vehicle.wait_init()

        while True:
            msg = self.vehicle.message_factory.command_long_encode(
                                                                                     0, 1,    # target system, target component
                                                                                     mavutil.mavlink.MAV_CMD_DO_CHANGE_SPEED, # frame
                                                                                     0,       # confirmation
                                                                                     1, 1.0, -1, # params 1-3
                                                                                     0.0, 0.0, 0.0, 0.0 ) # params 4-7 (not used)


            # send command to vehicle
            self.vehicle.send_mavlink(msg)

            msg2 = self.vehicle.message_factory.command_long_encode(
                                                        0, 1,    # target system, target component
                                                        mavutil.mavlink.MAV_CMD_DO_SET_ROI, #command
                                                        0, #confirmation
                                                        0, 0, 0, 0, #params 1-4
                                                        33.0,
                                                        100.9,
                                                        40.6
                                                        )

            self.vehicle.send_mavlink(msg2)
            time.sleep( 1 / UPDATE_RATE )

PerfTest()