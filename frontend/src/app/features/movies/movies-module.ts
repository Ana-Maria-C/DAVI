import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

import { MoviesRoutingModule } from './movies-routing-module';
import { MovieListComponent } from './pages/movie-list/movie-list';
import { FacetedSearchSidebarComponent } from './components/faceted-search-sidebar/faceted-search-sidebar.component';
import { SharedModule } from '../../shared/shared.module';
import { ComparisonModalComponent } from './components/comparison-modal';
import { MovieDetailsModalComponent } from './components/movie-details-modal';


@NgModule({
  declarations: [
    MovieListComponent,
    FacetedSearchSidebarComponent,
    ComparisonModalComponent,
    MovieDetailsModalComponent
  ],
  imports: [
    CommonModule,
    MoviesRoutingModule,
    SharedModule,
    FormsModule
  ]
})
export class MoviesModule { }
