import { Component, OnInit } from '@angular/core';
import { AnalysisService } from '../../../../core/services/analysis.service';
import { Observable, BehaviorSubject, combineLatest } from 'rxjs';
import { switchMap, map, shareReplay } from 'rxjs/operators';

@Component({
    standalone: false,
    selector: 'app-trend-analysis',
    templateUrl: './trend-analysis.component.html',
    styleUrls: ['./trend-analysis.component.scss']
})
export class TrendAnalysisComponent implements OnInit {

    mostFamousMovies$: Observable<any[]> | null = null;
    highestRatedMovies$: Observable<any[]> | null = null;

    // Year Selection
    selectedYearSubject = new BehaviorSubject<number>(new Date().getFullYear());
    selectedYear$ = this.selectedYearSubject.asObservable();

    yearlyTrends$: Observable<any> | null = null;

    availableYears: number[] = [];

    constructor(private analysisService: AnalysisService) {
        // Generate years from 1900 to current year
        const currentYear = new Date().getFullYear();
        for (let y = currentYear; y >= 1900; y--) {
            this.availableYears.push(y);
        }
    }

    ngOnInit(): void {
        this.mostFamousMovies$ = this.analysisService.getMostFamousMovies();
        this.highestRatedMovies$ = this.analysisService.getHighestRatedMovies();

        this.yearlyTrends$ = this.selectedYear$.pipe(
            switchMap(year => this.analysisService.getYearlyTrends(year)),
            shareReplay(1)
        );
    }

    onYearChange(year: string): void {
        this.selectedYearSubject.next(parseInt(year, 10));
    }
}
