import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { MoviesRoutingModule } from './movies-routing-module';
import { MovieListComponent } from './pages/movie-list/movie-list';
import { FacetedSearchSidebarComponent } from './components/faceted-search-sidebar/faceted-search-sidebar.component';
import { SharedModule } from '../../shared/shared.module';
import { ComparisonModalComponent } from './components/comparison-modal';


@NgModule({
  declarations: [
    MovieListComponent,
    FacetedSearchSidebarComponent,
    ComparisonModalComponent
  ],
  imports: [
    CommonModule,
    MoviesRoutingModule,
    SharedModule
  ]
})
export class MoviesModule { }
