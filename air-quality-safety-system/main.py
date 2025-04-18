def check_air_quality(CO2_level, smoke_density, co_level, gas_level, 
                      threshold_smoke=100, threshold_co=60, gas_threshold=250):
    # CO2 control
    if CO2_level >= 1000:
        print("Signal: Turn on exhaust fan (CO2 control)")
    elif CO2_level <= 800:
        print("Signal: Turn off exhaust fan (CO2 control)")
    else:
        print("Signal: Fan state stays as is (CO2 control)")

    # Smoke control
    if smoke_density > threshold_smoke and co_level < threshold_co:
        print("Signal: Turn on exhaust fan (Cooking smoke detected)")
    elif smoke_density > threshold_smoke and co_level > threshold_co:
        print("Signal: Turn on exhaust fan (Fire smoke detected)")
        print("Signal: Trigger alarm (Fire smoke detected)")
        print("Signal: Send email alerts using Firebase (Fire smoke detected)")

    # Gas leak detection
    if gas_level >= gas_threshold:
        print("Signal: Turn off gas appliances (Gas leak detected)")
        print("Signal: Close gas valve (Gas leak detected)")
        print("Signal: Turn on exhaust fan (Gas leak detected)")
        print("Signal: Trigger alarm (Gas leak detected)")
        print("Signal: Send email alerts using Firebase (Gas leak detected)")

# Example usage
# Replace these values with actual sensor readings and thresholds
check_air_quality(
    CO2_level=950, 
    smoke_density=120, 
    co_level=50, 
    gas_level=300, 
    threshold_smoke=100, 
    threshold_co=60, 
    gas_threshold=250
)
