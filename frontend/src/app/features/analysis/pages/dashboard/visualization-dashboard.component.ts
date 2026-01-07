import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { shareReplay } from 'rxjs/operators';
import { AnalysisService } from '../../../../core/services/analysis.service';

@Component({
    standalone: false,
    selector: 'app-visualization-dashboard',
    templateUrl: './visualization-dashboard.component.html',
    styleUrls: ['./visualization-dashboard.component.scss']
})
export class VisualizationDashboardComponent implements OnInit {
    statsData$: Observable<any> | null = null;

    constructor(private analysisService: AnalysisService) { }

    ngOnInit(): void {
        this.statsData$ = this.analysisService.getStatistics().pipe(
            shareReplay(1)
        );
    }
}
