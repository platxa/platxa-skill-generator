# shadcn/ui Component Reference

Pre-installed components available via `@/components/ui/{name}`.

## Layout Components

| Component | Named Exports | Radix Dependency |
|-----------|---------------|------------------|
| card | Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent | none |
| separator | Separator | @radix-ui/react-separator |
| scroll-area | ScrollArea, ScrollBar | @radix-ui/react-scroll-area |
| resizable | ResizablePanelGroup, ResizablePanel, ResizableHandle | react-resizable-panels |
| aspect-ratio | AspectRatio | @radix-ui/react-aspect-ratio |
| collapsible | Collapsible, CollapsibleTrigger, CollapsibleContent | @radix-ui/react-collapsible |
| sheet | Sheet, SheetTrigger, SheetContent, SheetHeader, SheetTitle, SheetDescription, SheetFooter, SheetClose | @radix-ui/react-dialog |

## Form Components

| Component | Named Exports | Radix Dependency |
|-----------|---------------|------------------|
| button | Button, buttonVariants | @radix-ui/react-slot |
| input | Input | none |
| textarea | Textarea | none |
| label | Label | @radix-ui/react-label |
| checkbox | Checkbox | @radix-ui/react-checkbox |
| radio-group | RadioGroup, RadioGroupItem | @radix-ui/react-radio-group |
| switch | Switch | @radix-ui/react-switch |
| slider | Slider | @radix-ui/react-slider |
| select | Select, SelectGroup, SelectValue, SelectTrigger, SelectContent, SelectLabel, SelectItem, SelectSeparator | @radix-ui/react-select |
| form | Form, FormItem, FormLabel, FormControl, FormDescription, FormMessage, FormField | react-hook-form |

## Data Display

| Component | Named Exports | Radix Dependency |
|-----------|---------------|------------------|
| table | Table, TableHeader, TableBody, TableFooter, TableHead, TableRow, TableCell, TableCaption | none |
| badge | Badge, badgeVariants | none |
| avatar | Avatar, AvatarImage, AvatarFallback | @radix-ui/react-avatar |
| progress | Progress | @radix-ui/react-progress |
| skeleton | Skeleton | none |
| calendar | Calendar | react-day-picker |
| carousel | Carousel, CarouselContent, CarouselItem, CarouselPrevious, CarouselNext | embla-carousel-react |

## Navigation

| Component | Named Exports | Radix Dependency |
|-----------|---------------|------------------|
| tabs | Tabs, TabsList, TabsTrigger, TabsContent | @radix-ui/react-tabs |
| navigation-menu | NavigationMenu, NavigationMenuList, NavigationMenuItem, NavigationMenuContent, NavigationMenuTrigger, NavigationMenuLink | @radix-ui/react-navigation-menu |
| menubar | Menubar, MenubarMenu, MenubarTrigger, MenubarContent, MenubarItem, MenubarSeparator, MenubarShortcut, MenubarGroup, MenubarSub, MenubarSubContent, MenubarSubTrigger | @radix-ui/react-menubar |
| breadcrumb | Breadcrumb, BreadcrumbList, BreadcrumbItem, BreadcrumbLink, BreadcrumbPage, BreadcrumbSeparator, BreadcrumbEllipsis | none |

## Overlays

| Component | Named Exports | Radix Dependency |
|-----------|---------------|------------------|
| dialog | Dialog, DialogTrigger, DialogContent, DialogHeader, DialogFooter, DialogTitle, DialogDescription, DialogClose | @radix-ui/react-dialog |
| dropdown-menu | DropdownMenu, DropdownMenuTrigger, DropdownMenuContent, DropdownMenuItem, DropdownMenuCheckboxItem, DropdownMenuRadioItem, DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuShortcut, DropdownMenuGroup, DropdownMenuSub, DropdownMenuSubContent, DropdownMenuSubTrigger, DropdownMenuRadioGroup | @radix-ui/react-dropdown-menu |
| context-menu | ContextMenu, ContextMenuTrigger, ContextMenuContent, ContextMenuItem, ContextMenuCheckboxItem, ContextMenuRadioItem, ContextMenuLabel, ContextMenuSeparator, ContextMenuShortcut, ContextMenuGroup, ContextMenuSub, ContextMenuSubContent, ContextMenuSubTrigger, ContextMenuRadioGroup | @radix-ui/react-context-menu |
| popover | Popover, PopoverTrigger, PopoverContent | @radix-ui/react-popover |
| hover-card | HoverCard, HoverCardTrigger, HoverCardContent | @radix-ui/react-hover-card |
| tooltip | Tooltip, TooltipTrigger, TooltipContent, TooltipProvider | @radix-ui/react-tooltip |
| command | Command, CommandDialog, CommandInput, CommandList, CommandEmpty, CommandGroup, CommandItem, CommandShortcut, CommandSeparator | cmdk |
| drawer | Drawer, DrawerTrigger, DrawerContent, DrawerHeader, DrawerFooter, DrawerTitle, DrawerDescription, DrawerClose | vaul |

## Feedback

| Component | Named Exports | Radix Dependency |
|-----------|---------------|------------------|
| alert | Alert, AlertTitle, AlertDescription | none |
| sonner | Toaster, toast | sonner |
| toast | Toast, ToastAction, ToastClose, ToastDescription, ToastProvider, ToastTitle, ToastViewport, useToast | @radix-ui/react-toast |

## Utility

| Component | Named Exports | Radix Dependency |
|-----------|---------------|------------------|
| accordion | Accordion, AccordionItem, AccordionTrigger, AccordionContent | @radix-ui/react-accordion |
| toggle | Toggle, toggleVariants | @radix-ui/react-toggle |
| toggle-group | ToggleGroup, ToggleGroupItem | @radix-ui/react-toggle-group |

## Utility Libraries

| Package | Import | Purpose |
|---------|--------|---------|
| clsx | `import { clsx } from "clsx"` | Conditional class joining |
| tailwind-merge | `import { twMerge } from "tailwind-merge"` | Merge Tailwind classes without conflicts |
| class-variance-authority | `import { cva, type VariantProps } from "class-variance-authority"` | Variant-based component styling |
| lucide-react | `import { Icon } from "lucide-react"` | Icon library (1000+ icons) |
| date-fns | `import { format } from "date-fns"` | Date formatting for Calendar |
| zod | `import { z } from "zod"` | Schema validation for Forms |
| react-hook-form | `import { useForm } from "react-hook-form"` | Form state management |
