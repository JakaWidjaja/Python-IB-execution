

random_number_path=/media/lun/Data2/Trading_Algo/class_c++/Random_Number/
volatility_path=/media/lun/Data2/Trading_Algo/class_c++/Volatility/
stochastic_model_path=/media/lun/Data2/Trading_Algo/class_c++/Stochastic_Model/
correlation_path=/media/lun/Data2/Trading_Algo/class_c++/Correlation/


g++  -std=c++14  -o main main.cpp \
"$stochastic_model_path""heston.cpp" \
"$stochastic_model_path""stochastic_model.cpp" \
"$volatility_path""volatility.cpp" \
"$volatility_path""market_implied.cpp" \
"$correlation_path""correlation.cpp" \
"$correlation_path""market_correlation.cpp" \
"$random_number_path""random_number.cpp" \
"$random_number_path""random_number_generator.cpp" \
"$random_number_path""pseudo_uniform_random.cpp" \
"$random_number_path""uniform_random_number.cpp" \
"$random_number_path""exponential_random.cpp"

./main



exit -0