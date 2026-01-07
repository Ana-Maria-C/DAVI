import { Component, OnInit } from '@angular/core';
import { AnalysisService, FacetData, FilterState } from '../../../../core/services/analysis.service';

@Component({
    standalone: false,
    selector: 'app-faceted-search-sidebar',
    templateUrl: './faceted-search-sidebar.component.html',
    styleUrls: ['./faceted-search-sidebar.component.scss']
})
export class FacetedSearchSidebarComponent implements OnInit {
    facets: FacetData | null = null;
    filters: FilterState = {};

    constructor(private analysisService: AnalysisService) { }

    ngOnInit(): void {
        this.analysisService.getFacets().subscribe(data => {
            this.facets = data;
        });

        this.analysisService.activeFilters$.subscribe(f => {
            this.filters = f;
        });
    }

    toggleGenre(genre: string) {
        if (this.filters.genre === genre) {
            this.filters.genre = undefined;
        } else {
            this.filters.genre = genre;
        }
        this.update();
    }

    updateYear(min: any, max: any) {
        const minVal = parseInt(min);
        const maxVal = parseInt(max);
        if (minVal > maxVal) return;
        this.filters.yearMin = minVal;
        this.filters.yearMax = maxVal;
        this.update();
    }

    updateRating(min: any, max: any) {
        const minVal = parseFloat(min);
        const maxVal = parseFloat(max);
        if (minVal > maxVal) return;
        this.filters.ratingMin = minVal;
        this.filters.ratingMax = maxVal;
        this.update();
    }

    private update() {
        this.analysisService.updateFilters({ ...this.filters });
    }
}
