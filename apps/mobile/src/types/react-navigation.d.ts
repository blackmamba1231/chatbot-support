import { ComponentType, ReactNode } from 'react';

// Import the RootStackParamList from App.tsx
import { RootStackParamList } from '../../App';

declare module '@react-navigation/native' {
  export interface NavigationState {
    index: number;
    routes: Array<{
      key: string;
      name: string;
      params?: any;
    }>;
  }

  export interface NavigationProp<ParamList = RootStackParamList> {
    navigate<RouteName extends keyof ParamList>(
      name: RouteName,
      params?: ParamList[RouteName]
    ): void;
    goBack(): void;
    addListener: (event: string, callback: () => void) => () => void;
    setParams(params: Partial<ParamList[keyof ParamList]>): void;
  }

  export interface RouteProp<ParamList = RootStackParamList, RouteName extends keyof ParamList = keyof ParamList> {
    key: string;
    name: RouteName;
    params: ParamList[RouteName];
  }

  export function useNavigation<T = NavigationProp>(): T;
  export function useRoute<T = RouteProp>(): T;
}
