#!/usr/bin/env node
import 'source-map-support/register';
import * as cdk from '@aws-cdk/core';
import { TempMetricsInfraStack } from '../lib/temp-metrics-infra-stack';

const app = new cdk.App();
new TempMetricsInfraStack(app, 'TempMetricsInfraStack');
