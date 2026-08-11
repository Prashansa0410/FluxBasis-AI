import {describe,it,expect} from 'vitest';import {render,screen} from '@testing-library/react';import {Stat} from './shell';
describe('Stat',()=>{it('renders value',()=>{render(<Stat label="Reliability" value="99%"/>);expect(screen.getByText('99%')).toBeTruthy();});});
