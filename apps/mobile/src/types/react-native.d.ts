declare module 'react-native' {
  import * as ReactNative from 'react-native';
  
  export interface StyleSheetStatic {
    create<T extends ReactNative.StyleSheet.NamedStyles<T> | ReactNative.StyleSheet.NamedStyles<any>>(styles: T | ReactNative.StyleSheet.NamedStyles<T>): T;
  }
  
  export const StyleSheet: StyleSheetStatic;
  
  export type ViewProps = ReactNative.ViewProps;
  export const View: React.ComponentType<ViewProps>;
  
  export type TextProps = ReactNative.TextProps;
  export const Text: React.ComponentType<TextProps>;
  
  export type TouchableOpacityProps = ReactNative.TouchableOpacityProps;
  export const TouchableOpacity: React.ComponentType<TouchableOpacityProps>;
  
  export type FlatListProps<ItemT> = ReactNative.FlatListProps<ItemT>;
  export class FlatList<ItemT = any> extends React.Component<FlatListProps<ItemT>> {}
  
  export type SafeAreaViewProps = ReactNative.SafeAreaViewProps;
  export const SafeAreaView: React.ComponentType<SafeAreaViewProps>;
  
  export type StatusBarProps = ReactNative.StatusBarProps;
  export const StatusBar: React.ComponentType<StatusBarProps>;
  
  export type TextInputProps = ReactNative.TextInputProps;
  export const TextInput: React.ComponentType<TextInputProps>;
  
  export type KeyboardAvoidingViewProps = ReactNative.KeyboardAvoidingViewProps;
  export const KeyboardAvoidingView: React.ComponentType<KeyboardAvoidingViewProps>;
  
  export type ActivityIndicatorProps = ReactNative.ActivityIndicatorProps;
  export const ActivityIndicator: React.ComponentType<ActivityIndicatorProps>;
  
  export type ImageProps = ReactNative.ImageProps;
  export const Image: React.ComponentType<ImageProps>;
  
  export const Platform: ReactNative.PlatformStatic;
}
