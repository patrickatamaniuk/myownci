Rpcserver::Application.routes.draw do

  devise_for :users,  :controllers => { :registrations => "users/registrations" }
  scope "/admin" do
    resources :users
  end

  namespace :api do
#    devise_for :users
    resources :requests, :only => [:index, :show]
  end

  resources :token_authentications, :only => [:create, :destroy]

  resources :jobs

  resources :requests, :only => [:index, :show, :destroy]

  resources :metals, :only => [:index, :show, :destroy]

  resources :workers

  root :to => "home#index"
end
