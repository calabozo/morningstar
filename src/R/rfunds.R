library('tidyverse',quietly=TRUE, warn.conflicts=FALSE)
library(zoo,quietly=TRUE, warn.conflicts=FALSE)
library(reshape2,quietly=TRUE, warn.conflicts=FALSE)
library(pracma,quietly=TRUE, warn.conflicts=FALSE)

calc_roi <- function(df, num_days=365, annual_charges_percentage=NULL){
    df  %>% arrange(date) %>% mutate_at(vars(-date),~./lag(.,num_days))
    if (!is.null(annual_charges_percentage)){
        df<-df-repmat(as.matrix(annual_charges_percentage,nrow=1),nrow(df),1)*num_days/365/100
    }
}
calc_consecutive_losses <- function(df_roi,max_days_with_losses=150){
    df <- df_roi %>% select(-date) %>% mutate_all(~.<1)
    num_consecutive_days_with_losses<-apply(df,2,function(x) with(rle(x), max(lengths[values],na.rm=T)))    
    names(num_consecutive_days_with_losses[num_consecutive_days_with_losses<max_days_with_losses])
}
calc_summary <- function(df_values, num_days=365){
    df_roi <- calc_roi(df_values, num_days)
    mean_roi<-df_roi %>% select(-date) %>% colMeans(na.rm=T)
    geom_mean_roi<-df_roi %>% select(-date) %>% mutate_all(log) %>% colMeans(na.rm=T) %>% exp()
    var_roi<-df_roi %>% select(-date) %>% apply(2,var,na.rm=T)
    df_summary<-data.frame(isin=names(mean_roi),mean=mean_roi,geom=geom_mean_roi,var=var_roi)

    df_min_date<-na.omit(melt(df_values, id.vars='date',variable.name='isin')) %>% group_by(isin) %>% summarise(mindate=min(date), .groups = 'drop')
    df_summary<-merge(df_summary,df_min_date,by='isin')
    df_summary$isin<-as.character(df_summary$isin)

    df <- df_roi %>% select(-date) %>% mutate_all(~.<1)
    num_consecutive_days_with_losses<-apply(df,2,function(x) with(rle(x), max(lengths[values],na.rm=T)))
    df_summary<-merge(df_summary,data.frame(days_losses=num_consecutive_days_with_losses,isin=names(num_consecutive_days_with_losses)),by='isin')
    rownames(df_summary)<-df_summary$isin
    df_summary$isin<-NULL
    df_summary
}
plot_funds <- function(df_values,funds=NULL,start_date=NULL){
    if (!is.null(start_date)){
        df_values<-df_values %>% filter(date>=start_date)
        df_values_no_date<-df_values %>% select(-date)
        df_values_no_date<-df_values_no_date/repmat(as.matrix(df_values_no_date[1,]),nrow(df_values_no_date),1)
        df_values_no_date$date<-df_values$date
        df_values<-df_values_no_date
    }    
    if (!is.null(funds)){
        df <- df_values[,c("date",funds)]
    }else{
        df <- df_values
        funds <- colnames(df)[colnames(df)!="date"]
    }
    df <- df[rowSums(is.na(df)) != length(funds), ]
    ggplot(melt(df, id.vars='date',variable.name='ISIN'),
       aes(x=date,y=value,color=ISIN))+geom_line()
}
calc_optim<-function(df_subset, variance_importance=100){
    x0<-rep(1/ncol(df_subset),ncol(df_subset))

    roi_optim<-function(coefs){
        mn<-mean(rowSums(repmat(coefs,nrow(df_subset),1) * df_subset))
        vr<-var(rowSums(repmat(coefs,nrow(df_subset),1) * df_subset))
        return (-mn/exp(1+variance_importance*vr))
        #return(mn)
    }
    constrain_func<-function(coefs){
        sum(coefs)
    }


    lx <- rep(0,length(x0))
    ux <- rep(1,length(x0))
    sol1 <- Rsolnp::solnp(x0, fun = roi_optim, eqfun = constrain_func, eqB = 1, LB=lx, UB=ux)
    coefs<-sol1$pars    
    names(coefs)<-colnames(df_subset)
    coefs<-round(coefs[coefs>1e-2],4)
    coefs<-coefs/sum(coefs)
    return(coefs)
}
simulate_investment<-function(df_value,coefs){
    df<-df_value[,names(coefs)]
    idx<-na.action(na.omit(df))
    if (length(idx)>0){df<-df[-idx,]}
    df$combined<-rowSums(repmat(coefs,nrow(df),1) * df)
    df<-df/repmat(as.matrix(df[1,]),nrow(df),1)
    if (length(idx)>0){
        df$date<-df_value$date[-idx]
    }else{
        df$date<-df_value$date
    }
    df
}

