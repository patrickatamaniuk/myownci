Rpcserver::Application.routes.draw do

  devise_for :users,  :controllers => { :registrations => "users/registrations" }
  scope "/admin" do
    resources :users
  end

  resources :token_authentications, :only => [:create, :destroy]

  resources :jobs, :only => [:index, :show, :destroy]

  resources :requests, :only => [:index, :show, :destroy]

  resources :metals, :only => [:index, :show, :destroy]

  resources :workers, :only => [:index, :show, :edit, :update, :destroy]

  root :to => "home#index"
end
