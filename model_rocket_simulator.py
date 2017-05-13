accel = 0
v = 0
max_v = 0
apogee = 0
time = 0
alt = 0

def simulate_time_step(m, v, f, d, alt, t):
    accel = (f - d*v**2)/m - 9.81456
    v += accel*t
    alt += v*t
    return(alt, v, accel)
#simulate_flight will simulate a rocket flight
#the inputs are:
#ef = list of thrust at every time step
#em = list of engine mass at every time step
#cd = drag coefficient
#btd = body tube diameter
#rm = rocket mass without engine
#et = time per time step
def simulate_flight(ef, em, cd, btd, rm, et, c_mass):
    rmwe = rm
    max_accel = 0
    rm *= 0.0283495
    btd *= .001
    cou = False
    pi = 3.141592653
    rho = 1.2062
    t = 0
    v = 0
    accel = 0
    alt = 0
    total_time = 0
    while True:
        try:
            f = ef[t]
            rmwe = em[t]
        except:
            f = 0
            rmwe = rm + c_mass
        try:
            tps = et[t]
        except:
            tps = .00001
        d = .5 * rho * pi * cd * (.5 * btd) ** 2
        l = simulate_time_step(rm, v, f, d, alt, tps)
        alt = l[0]
        v = l[1]
        accel = l[2]
        t += 1
        total_time += tps
     #   print(total_time)
      #  print(alt, v, accel)
        if accel < 0 and cou == False:
            max_vel = v
            cou = True
        if max_accel < accel:
            max_accel = accel
        if v < 0:
            apogee = alt
            break
    apogee *= 3.28084
    max_vel *= 2.23694
    max_accel *= 0.101972
    return apogee, max_vel, max_accel


def parse_engine_file(eng):
    count = 0
    thrust = []
    time_list = []
    time = 0
    weight = []
    d = 0
    for l in eng:
        if l[0] != ';':
            d += 1
            if d == 1:
                l = l.split(' ')
                p_weight = float(l[4])
                t_weight = float(l[5])
                break
    for l in eng:
        if l[0] != ';':
            d += 1
        if d > 1:
            l = l.split()
            new_time = float(l[0])
            time_this_step = new_time - time
            time_list.append(time_this_step)
            time = new_time
            thrust.append(float(l[1]))
            if float(l[1]) == 0:
                total_time = float(l[0])

    for t in time_list:
        count += t
        try:
            p_mass = (total_time / (total_time - count)) * p_weight
        except:
            p_mass = 0
        t_mass = p_mass + t_weight - p_weight
        weight.append(t_mass)
    c_mass = t_weight - p_mass

    return [time_list, thrust, weight, c_mass]
    
engine = open('C:\\Users\\Noah\\Documents\\engine files\\Estes_C6.eng', 'r')
e = parse_engine_file(engine)
ef = e[1]
em = e[2]
et = e[0]
fl = simulate_flight(ef, em, .87, 24.1, 1.42, et, 0)
print(fl)
