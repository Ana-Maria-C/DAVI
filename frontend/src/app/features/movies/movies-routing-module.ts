import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { MovieListComponent } from './pages/movie-list/movie-list';

const routes: Routes = [
  { path: '', component: MovieListComponent },
  { path: ':id', component: MovieListComponent }
];

@NgModule({
  imports: [RouterModule.forChild(routes)],
  exports: [RouterModule]
})
export class MoviesRoutingModule { }
