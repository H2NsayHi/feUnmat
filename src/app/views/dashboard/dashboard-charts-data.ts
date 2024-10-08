import { Injectable } from '@angular/core';
import {
  ChartData,
  ChartDataset,
  ChartOptions,
  ChartType,
  PluginOptionsByType,
  ScaleOptions,
  TooltipLabelStyle
} from 'chart.js';
import { DeepPartial } from 'chart.js/dist/types/utils';
import { getStyle, hexToRgba } from '@coreui/utils';

export interface IChartProps {
  data?: ChartData;
  labels?: any;
  options?: ChartOptions;
  colors?: any;
  type: ChartType;
  legend?: false;

  [propName: string]: any;
}

@Injectable({
  providedIn: 'any'
})
export class DashboardChartsData {
  constructor() {
    this.initMainChart();
  }

  public mainChart: IChartProps = { type: 'line' };

  public random(min: number, max: number) {
    return Math.floor(Math.random() * (max - min + 1) + min);
  }

  initMainChart(period: string = 'Month', customData: number[] = []): IChartProps {
    const brandInfo = getStyle('--cui-info') ?? '#20a8d8';
    const brandInfoBg = hexToRgba(brandInfo, 10);
  
    // Use custom data if provided, otherwise default to random data
    const data = customData.length ? customData : Array(12).fill(0).map(() => this.random(10, 30));
  
    const datasets: ChartDataset[] = [
      {
        data,
        label: '',
        backgroundColor: brandInfoBg,
        borderColor: brandInfo,
        pointHoverBackgroundColor: brandInfo,
        borderWidth: 2,
        fill: false
      }
    ];
  

    const labels = Array.from({ length: data.length }, (_, i) => (i + 1).toString());
  
    const scales = this.getScales();

    const plugins: DeepPartial<PluginOptionsByType<any>> = {

      legend: {
        display: false // Hide the legend (annotation)
      },
      tooltip: {
        enabled: false,
        // callbacks: {
        //   labelColor: (context) => ({ backgroundColor: context.dataset.borderColor } as TooltipLabelStyle)
        // }
      },
      

    };
  
    const options: ChartOptions = {
      maintainAspectRatio: false,
      plugins,
      scales,
      elements: {
        line: {
          tension: 0.4
        },
        point: {
          radius: 0,
          hitRadius: 10,
          hoverRadius: 4,
          hoverBorderWidth: 3
        }
      }
    };
  
    return {
      type: 'line',
      data: {
        labels,
        datasets
      },
      options
    };
  }
  

  getScales() {
    const colorBorderTranslucent = getStyle('--cui-border-color-translucent');
    const colorBody = getStyle('--cui-body-color');
  
    const scales: ScaleOptions<any> = {
      x: {
        grid: {
          color: colorBorderTranslucent,
          drawOnChartArea: false
        },
        ticks: {
          color: colorBody
        }
      },
      y: {
        border: {
          color: colorBorderTranslucent
        },
        grid: {
          color: colorBorderTranslucent
        },
        beginAtZero: true, // Ensures y-axis starts at 0
        ticks: {
          color: colorBody,
          // Explicitly define the 'value' type as 'number'
          callback: (value: number) => value.toString() // Display values directly as is
        }
      }
    };

    return scales;
  }
  
  
}
