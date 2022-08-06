import folium

gps_list = []
with open("track1.txt" ,"r" )as file:
    for elem in file:
        i = 0
        #print(elem)
        raw_str = elem.strip()
        raw_list = list(raw_str.split(","))
        time_data = (raw_list[0:4])
        lat = raw_list[4].replace("Latitude: ","").strip()
        lon = raw_list[5].replace("Longitude: ","").strip()
        alt = raw_list[6].replace("Altitude: ","").strip()
        vib = raw_list[14].strip()
        #gps_data = time_data, lat,lon,alt,vib
        gps_data = (float(lat), float(lon))#,float(vib))
        gps_list.append(gps_data)


print(gps_list)



m = folium.Map(location=gps_list[0],
              zoom_start=15)

loc = gps_list
folium.PolyLine(loc,
                color='red',
                weight=15,
                opacity=0.8).add_to(m)
m
m.save('route.html')