import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { NgxChartsModule } from '@swimlane/ngx-charts';
import { FormsModule } from '@angular/forms';

import { VisualizationDashboardComponent } from './pages/dashboard/visualization-dashboard.component';
import { StatsChartComponent } from './components/stats-chart/stats-chart.component';
import { NetworkGraphComponent } from './components/network-graph/network-graph.component';
import { TrendAnalysisComponent } from './pages/trends/trend-analysis.component';

const routes: Routes = [
    { path: '', component: VisualizationDashboardComponent }
];

@NgModule({
    declarations: [
        VisualizationDashboardComponent,
        StatsChartComponent,
        NetworkGraphComponent,
        TrendAnalysisComponent
    ],
    imports: [
        CommonModule,
        RouterModule.forChild(routes),
        NgxChartsModule,
        FormsModule
    ]
})
export class AnalysisModule { }
