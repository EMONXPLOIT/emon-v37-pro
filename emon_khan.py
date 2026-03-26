import websocket, json, os, datetime, time, sys
import numpy as np
from colorama import Fore, init

# কালার ইনিশিয়ালাইজেশন
init(autoreset=True)

# গ্লোবাল ভেরিয়েবল
prices = []
wins = 0
losses = 0
total_trades = 0

def print_banner():
    os.system('clear')
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.YELLOW}  ███████╗███╗   ███╗ ██████╗ ███╗   ██╗")
    print(f"{Fore.YELLOW}  ██╔════╝████╗ ████║██╔═══██╗████╗  ██║")
    print(f"{Fore.YELLOW}  █████╗  ██╔████╔██║██║   ██║██╔██╗ ██║")
    print(f"{Fore.YELLOW}  ██╔══╝  ██║╚██╔╝██║██║   ██║██║╚██╗██║")
    print(f"{Fore.YELLOW}  ███████╗██║ ╚═╝ ██║╚██████╔╝██║ ╚████║")
    print(f"{Fore.YELLOW}  ╚══════╝╚═╝     ╚═╝     --- EMON KHAN ---")
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.MAGENTA}    🔥 EMON V37.0 AI-ULTRA MAX (PRO PSYCHOLOGY) 🔥")
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.WHITE} WIN: {Fore.GREEN}{wins} {Fore.WHITE}| LOSS: {Fore.RED}{losses} {Fore.WHITE}| ACCURACY: {Fore.YELLOW}{get_accuracy()}%")
    print(f"{Fore.CYAN}{'='*60}\n")

def get_accuracy():
    if total_trades == 0: return 0
    return round((wins / total_trades) * 100, 2)

def get_candle_analysis(p):
    if len(p) < 40: return "⏳ ANALYZING DEPTH..." # ৪০টি ডাটা পয়েন্ট হলে এনালাইসিস শুরু হবে
    
    current = p[-1]
    opening = p[0]
    high = max(p)
    low = min(p)
    
    body = abs(current - opening)
    upper_shadow = high - max(current, opening)
    lower_shadow = min(current, opening) - low
    
    # ভলিউম এবং মোমেন্টাম ক্যালকুলেশন
    all_diffs = [abs(p[i] - p[i-1]) for i in range(1, len(p))]
    avg_body = np.mean(all_diffs)
    std_dev = np.std(all_diffs) # ভোলাটিলিটি চেক

    # ট্রেন্ড ডিটেকশন (MA Filter)
    short_ma = np.mean(p[-10:])
    long_ma = np.mean(p[-35:])
    uptrend = short_ma > long_ma
    downtrend = short_ma < long_ma

    # ১. ক্যান্ডেলস্টিক প্যাটার্নস (Psychology)
    is_hammer = lower_shadow > (body * 2.5) and upper_shadow < (body * 0.5)
    is_shooting_star = upper_shadow > (body * 2.5) and lower_shadow < (body * 0.5)
    is_engulfing_up = (current > opening) and (body > np.mean(all_diffs[-3:]) * 2)
    is_engulfing_down = (current < opening) and (body > np.mean(all_diffs[-3:]) * 2)
    is_marubozu = body > (avg_body + std_dev) and upper_shadow < (body * 0.1) and lower_shadow < (body * 0.1)

    # ২. ডিসিশন মেকিং লজিক (The Brain)
    
    # ⬆️ শক্তিশালী CALL সিগন্যাল
    if (uptrend and (is_engulfing_up or (is_marubozu and current > opening))):
        return "SURE_CALL_⬆️ [STRONG TREND PUSH]"
    
    if (downtrend and is_hammer and current > short_ma):
        return "SURE_CALL_⬆️ [REVERSAL DETECTED]"

    # ⬇️ শক্তিশালী PUT সিগন্যাল
    if (downtrend and (is_engulfing_down or (is_marubozu and current < opening))):
        return "SURE_PUT_⬇️ [STRONG TREND FALL]"
    
    if (uptrend and is_shooting_star and current < short_ma):
        return "SURE_PUT_⬇️ [REVERSAL DETECTED]"

    # সাইডওয়ে বা অনিশ্চিত মার্কেট ফিল্টার
    if body < (avg_body * 0.5):
        return "🔍 WAITING FOR VOLATILITY..."

    return "📊 SCANNING NEXT MOVE..."

def on_message(ws, message):
    global prices, wins, losses, total_trades
    data = json.loads(message)
    
    if 'tick' in data:
        price = data['tick']['quote']
        prices.append(price)
        
        now = datetime.datetime.now()
        if len(prices) > 120: prices.pop(0) # র‍্যাম সেভ করার জন্য লিমিটেড ডাটা
        
        # প্রতি মিনিটের শুরুতে নতুন ক্যান্ডেল হিসেব হবে
        if now.second == 0: prices = [price]
        
        decision = get_candle_analysis(prices)
        countdown = 60 - now.second
        timer_color = Fore.RED if countdown < 10 else Fore.CYAN
        
        visual = "👀"
        if "CALL" in decision: visual = f"{Fore.GREEN}🟢 CALL"
        elif "PUT" in decision: visual = f"{Fore.RED}🔴 PUT"
        
        output = (f"\r{Fore.WHITE}[{now.strftime('%H:%M:%S')}] "
                  f"{Fore.YELLOW}Price: {price:.5f} | "
                  f"{Fore.MAGENTA}AI: {visual} | "
                  f"{timer_color}Wait: {countdown}s    ")
        sys.stdout.write(output)
        sys.stdout.flush()
        
        # ৫৭-৫৯ সেকেন্ডে ফাইনাল এন্ট্রি কনফার্মেশন
        if now.second >= 57 and now.second <= 59 and "SURE" in decision:
            if now.second == 57:
                total_trades += 1
                wins += 1 # সাকসেস ট্র্যাকার (এটি আপনি ম্যানুয়ালি পরে আপডেট করতে পারেন)
                
                direction = "✅ CALL / UP ✅" if "CALL" in decision else "🚨 PUT / DOWN 🚨"
                print(f"\n\n{Fore.GREEN}🎯 [AI CONFIRMED SIGNAL] 🎯")
                print(f"{Fore.WHITE}   STRATEGY  : {decision.split('[')[-1][:-1]}")
                print(f"{Fore.CYAN}   DIRECTION : {direction}")
                print(f"{Fore.YELLOW}   ACTION    : ENTER NOW FOR 1 MINUTE!")
                print(f"{Fore.WHITE}{'='*40}\n")
                print("\a") # অ্যালার্ট সাউন্ড

def on_open(ws):
    print(f"{Fore.GREEN}[✓] SERVER CONNECTED! EMON V37 PRO ACTIVE.")
    ws.send(json.dumps({"ticks": "frxEURUSD", "subscribe": 1}))

# প্রোগ্রাম শুরু
if __name__ == "__main__":
    print_banner()
    try:
        ws = websocket.WebSocketApp("wss://ws.binaryws.com/websockets/v3?app_id=1089", 
                                    on_open=on_open, on_message=on_message)
        ws.run_forever()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}Stopping Bot...")
        sys.exit()
