import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';

import { ResourceViewerRoutingModule } from './resource-viewer-routing.module';
import { ResourceDetailComponent } from './pages/resource-detail/resource-detail.component';
import { SharedModule } from '../../shared/shared.module';


@NgModule({
  declarations: [
    ResourceDetailComponent
  ],
  imports: [
    CommonModule,
    ResourceViewerRoutingModule,
    SharedModule
  ]
})
export class ResourceViewerModule { }
