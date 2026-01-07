import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterModule, Routes } from '@angular/router';
import { NgxChartsModule } from '@swimlane/ngx-charts';

import { VisualizationDashboardComponent } from './pages/dashboard/visualization-dashboard.component';
import { StatsChartComponent } from './components/stats-chart/stats-chart.component';

const routes: Routes = [
    { path: '', component: VisualizationDashboardComponent }
];

@NgModule({
    declarations: [
        VisualizationDashboardComponent,
        StatsChartComponent
    ],
    imports: [
        CommonModule,
        RouterModule.forChild(routes),
        NgxChartsModule
    ]
})
export class AnalysisModule { }
