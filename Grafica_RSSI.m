% Cargar datos desde el archivo Excel
filename = 'MedicionRSSI2.xlsx'; % Asegúrate de que el archivo esté en el mismo directorio del script
data = readtable(filename);

% Extraer las columnas necesarias
D = data.Distancia_m_; % Distancia en metros
Promedio = data.PromedioRSSI_dBm_; % Promedio de RSSI en dBm
Desviacion = data.Desviaci_nEst_ndar_dBm_; % Desviación estándar en dBm

% Si hay más mediciones individuales, cargarlas también
valores_individuales = table2array(data(:, 4:end)); % Tomamos desde la 4ta columna en adelante

% Crear la figura
figure; hold on;

% Graficar los valores individuales como puntos dispersos
plot(repmat(D, 1, size(valores_individuales, 2)), valores_individuales, 'ko', 'MarkerSize', 4, 'DisplayName', 'Valores individuales');

% Graficar el promedio con barras de error
errorbar(D, Promedio, Desviacion, 'd', 'MarkerFaceColor', 'r', 'MarkerEdgeColor', 'r', ...
         'Color', 'b', 'CapSize', 5, 'LineWidth', 1.5, 'DisplayName', 'Promedio ± Desviación estándar');

% Interpolación para suavizar la curva del promedio
D_smooth = linspace(min(D), max(D), 100); % Genera más puntos entre los valores originales
Promedio_smooth = interp1(D, Promedio, D_smooth, 'spline'); % Interpola suavizando la curva

% Graficar la curva suavizada del promedio
plot(D_smooth, Promedio_smooth, '-r', 'LineWidth', 2, 'DisplayName', 'Tendencia suavizada');

% Personalizar el gráfico
xlabel('Distancia (m)');
ylabel('RSSI (dBm)');
title('Medición de RSSI en función de la distancia');
grid on;
legend('show', 'Location', 'best');

% Mostrar la gráfica
hold off;
