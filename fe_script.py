from dronekit import connect, VehicleMode, LocationGlobalRelative
import time


# ウェイポイント
waypoints = {
    1: {'lat': 35.8791612185214817, 'long': 140.339347422122955, 'alt': 20, 'timesleep': 20},
    2: {'lat': 35.8789525840509356, 'long': 140.339042991399765, 'alt': 20, 'timesleep': 15},
    3: {'lat': 35.8790492948894482, 'long': 140.339427888393402, 'alt': 20, 'timesleep': 15},
    4: {'lat': 35.8788221872277973, 'long': 140.339182466268539, 'alt': 20, 'timesleep': 15},
    5: {'lat': 35.8789417176572059, 'long': 140.339532494544983, 'alt': 20, 'timesleep': 15},
    6: {'lat': 35.8787146096871084, 'long': 140.339320600032806, 'alt': 20, 'timesleep': 15},
    7: {'lat': 35.8788526131723913, 'long': 140.339646488428116, 'alt': 20, 'timesleep': 15},
    8: {'lat': 35.8791275327847856, 'long': 140.339684039354324, 'alt': 15, 'timesleep': 20},
}

# ウェイポイント移動
def gotoWP(wp_num):
    lat = waypoints[wp_num]['lat']
    long = waypoints[wp_num]['long']
    alt = waypoints[wp_num]['alt']

    wp = LocationGlobalRelative(lat, long, alt)
    vehicle.simple_goto(wp)
    time.sleep(waypoints[wp_num]['timesleep'])


# 接続
vehicle = connect('tcp:127.0.0.1:5762', wait_ready=True, timeout=60)

# ホームロケーション取得（緊急時RTL用）
while not vehicle.home_location:
    cmds = vehicle.commands
    cmds.download()
    cmds.wait_ready()
    if not vehicle.home_location:
        print("Waiting for home location ...")
#ホームロケーションの取得完了
print("Home location: %s " % vehicle.home_location)

try:
    # ARM準備
    vehicle.wait_for_armable()
    print("Waiting for araming ...")

    # モード変更
    vehicle.wait_for_mode("GUIDED")
    print("Mode changed: GUIDED")

    # グラウンドスピードを3.2m/sに設定 
    vehicle.groundspeed = 3.2
    
    # ARM
    vehicle.arm()
    print("ARMED!!")
    time.sleep(1)

    #離陸 
    print("Taking off ...")
    vehicle.wait_simple_takeoff(20, timeout=60)
    
except TimeoutError as takeoffError:
    print("Takeoff is timeout")


try:
    # Mission実行
    for wp in waypoints:
        gotoWP(wp)
    # 着陸
    vehicle.mode = VehicleMode("LAND")
    print("Mode changed: LAND")

except TimeoutError as gotoWPError:
    print("gotoWP is timeout")
    vehicle.mode = VehicleMode("RTL")
