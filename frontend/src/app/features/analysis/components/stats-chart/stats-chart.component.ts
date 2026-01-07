import { Component, Input, OnChanges } from '@angular/core';

@Component({
    standalone: false,
    selector: 'app-stats-chart',
    templateUrl: './stats-chart.component.html',
    styleUrls: ['./stats-chart.component.scss']
})
export class StatsChartComponent implements OnChanges {
    @Input() stats: any;

    genreData: any[] = [];
    ratingData: any[] = [];

    // Chart Options
    showXAxis = true;
    showYAxis = true;
    gradient = false;
    showLegend = true;
    showXAxisLabel = true;
    xAxisLabel = 'Genre';
    showYAxisLabel = true;
    yAxisLabelDistribution = 'Movies';
    yAxisLabelRating = 'Avg Rating';
    colorScheme: any = {
        domain: ['#5AA454', '#A10A28', '#C7B42C', '#AAAAAA', '#ff9800', '#2196f3']
    };

    ngOnChanges(): void {
        if (this.stats) {
            this.genreData = [...this.stats.genreDistribution];
            this.ratingData = [...this.stats.genreRatings];
        }
    }
}
