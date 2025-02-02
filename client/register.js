import { register } from 'ts-node';
import { pathToFileURL } from 'url';

register({
  project: './tsconfig.json',
  transpileOnly: true,
});

import(pathToFileURL('./server/server.ts').href);
